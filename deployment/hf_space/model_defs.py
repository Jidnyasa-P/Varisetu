"""
VariSetu Space — model architectures + preprocessing.

These class definitions are copied to match Model1_CrowdDensity/backend/model_loader.py,
Model2_Fall_Detection/backend/model_loader.py + preprocessing.py, and
Model3_Person_Reidentification/.../model_loader.py + preprocessing.py exactly.
This MUST stay byte-for-byte consistent with what was trained, or
load_state_dict() will fail or silently load wrong weights.
"""

import math
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms as T
from torchvision.models import resnet50


# =============================================================================
# Model 1 — Crowd Density (CSRNet)
# =============================================================================

class CSRNet(nn.Module):
    def __init__(self):
        super().__init__()
        frontend_cfg = [64, 64, "M", 128, 128, "M", 256, 256, 256, "M", 512, 512, 512]
        backend_cfg = [512, 512, 512, 256, 128, 64]
        self.frontend = self._make_layers(frontend_cfg, in_channels=3)
        self.backend = self._make_layers(backend_cfg, in_channels=512, dilation=2)
        self.output_layer = nn.Conv2d(64, 1, kernel_size=1)

    @staticmethod
    def _make_layers(cfg, in_channels, dilation=1):
        layers = []
        d_rate = dilation
        for v in cfg:
            if v == "M":
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=d_rate, dilation=d_rate)
                layers += [conv2d, nn.ReLU(inplace=True)]
                in_channels = v
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.frontend(x)
        x = self.backend(x)
        x = self.output_layer(x)
        return x


def _round_down_to_multiple_of_8(value: int) -> int:
    return max(8, (value // 8) * 8)


def build_crowd_transform(config: dict):
    max_dim = config["preprocessing"]["max_dimension"]
    mean = config["preprocessing"]["normalize_mean"]
    std = config["preprocessing"]["normalize_std"]
    normalize = T.Compose([T.ToTensor(), T.Normalize(mean, std)])

    def transform(pil_image: Image.Image):
        orig_size = pil_image.size
        w, h = orig_size
        scale = min(1.0, max_dim / max(w, h))
        new_w, new_h = _round_down_to_multiple_of_8(int(w * scale)), _round_down_to_multiple_of_8(int(h * scale))
        resized = pil_image.resize((new_w, new_h), Image.BILINEAR)
        return normalize(resized), orig_size

    return transform


class CrowdDensityModelBundle:
    def __init__(self, model, config, device, transform):
        self.model, self.config, self.device, self.transform = model, config, device, transform

    @classmethod
    def load(cls, weights_path: str, config: dict, device: str = "cpu"):
        device = torch.device(device)
        model = CSRNet().to(device)
        state_dict = torch.load(weights_path, map_location=device)
        model.load_state_dict(state_dict)
        model.eval()
        return cls(model, config, device, build_crowd_transform(config))

    @torch.no_grad()
    def predict(self, pil_image):
        x, orig_size = self.transform(pil_image)
        x = x.unsqueeze(0).to(self.device)
        raw_density = self.model(x)
        count = float(raw_density.sum().item())
        return count


# =============================================================================
# Model 2 — Fall / Medical-Distress Detection (BiLSTM + Attention over MediaPipe pose)
# =============================================================================

class AttentionPool(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.Linear(dim, 1)

    def forward(self, x):
        w = torch.softmax(self.attn(x).squeeze(-1), dim=1)
        return torch.bmm(w.unsqueeze(1), x).squeeze(1), w


class FallDetectionModel(nn.Module):
    def __init__(self, feat_dim: int, hidden: int = 128, num_layers: int = 2, dropout: float = 0.35):
        super().__init__()
        self.input_norm = nn.LayerNorm(feat_dim)
        self.lstm = nn.LSTM(feat_dim, hidden, num_layers=num_layers, batch_first=True,
                             bidirectional=True, dropout=dropout if num_layers > 1 else 0.0)
        self.pool = AttentionPool(hidden * 2)
        self.drop = nn.Dropout(dropout)
        self.binary_head = nn.Linear(hidden * 2, 1)
        self.stage_head = nn.Linear(hidden * 2, 3)

    def forward(self, x):
        x = self.input_norm(x)
        out, _ = self.lstm(x)
        pooled, attn_w = self.pool(out)
        pooled = self.drop(pooled)
        return self.binary_head(pooled).squeeze(-1), self.stage_head(pooled), attn_w


class FallModelBundle:
    def __init__(self, model, config, device):
        self.model, self.config, self.device = model, config, device
        self.window_size = config["input_window_frames"]
        self.stride = config["input_stride_frames"]
        self.feat_dim = config["feature_dim_per_frame"]
        self.feature_mean = config["feature_mean"]
        self.feature_std = config["feature_std"]
        self.threshold = config["recommended_binary_threshold"]

    @classmethod
    def load(cls, weights_path: str, config: dict, device: str = "cpu"):
        torch_device = torch.device(device)
        checkpoint = torch.load(weights_path, map_location=torch_device)
        model = FallDetectionModel(
            feat_dim=config["feature_dim_per_frame"],
            hidden=config.get("hidden_size", 128),
            num_layers=config.get("num_lstm_layers", 2),
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(torch_device)
        model.eval()
        return cls(model, config, torch_device)

    @torch.no_grad()
    def classify_window(self, window: np.ndarray):
        mean = np.asarray(self.feature_mean, dtype=np.float32)
        std = np.asarray(self.feature_std, dtype=np.float32)
        norm = (window - mean) / std
        x = torch.from_numpy(norm).float().unsqueeze(0).to(self.device)
        logit_b, logit_m, _ = self.model(x)
        prob_fall = torch.sigmoid(logit_b).item()
        stage_probs = torch.softmax(logit_m, dim=-1).squeeze(0).cpu().numpy().tolist()
        stage_labels = ["no_fall", "falling", "fallen"]
        return {
            "fall_probability": round(float(prob_fall), 4),
            "fall_detected": prob_fall >= self.threshold,
            "stage": stage_labels[int(np.argmax(stage_probs))],
        }


# =============================================================================
# Model 3a — Person Re-Identification (ResNet50 + BNNeck)
# =============================================================================

class ReIDModel(nn.Module):
    def __init__(self, num_classes: int, embedding_dim: int = 2048):
        super().__init__()
        backbone = resnet50(weights=None)
        backbone.layer4[0].downsample[0].stride = (1, 1)
        backbone.layer4[0].conv2.stride = (1, 1)
        self.backbone = nn.Sequential(*list(backbone.children())[:-2])
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.bnneck = nn.BatchNorm1d(embedding_dim)
        self.bnneck.bias.requires_grad_(False)
        self.classifier = nn.Linear(embedding_dim, num_classes, bias=False)

    def forward(self, x):
        feat_map = self.backbone(x)
        pooled = self.gap(feat_map).flatten(1)
        bn_feat = self.bnneck(pooled)
        logits = self.classifier(bn_feat)
        return pooled, bn_feat, logits


def build_reid_transform(config: dict):
    height, width = config["img_size"]["height"], config["img_size"]["width"]
    mean, std = config["normalize_mean"], config["normalize_std"]
    return T.Compose([T.Resize((height, width)), T.ToTensor(), T.Normalize(mean, std)])


class ReIDModelBundle:
    def __init__(self, model, config, device, transform):
        self.model, self.config, self.device, self.transform = model, config, device, transform
        self.verification_threshold = config.get("verification_threshold_at_5pct_fpr")

    @classmethod
    def load(cls, weights_path: str, config: dict, device: str = "cpu"):
        device = torch.device(device)
        model = ReIDModel(num_classes=config["num_train_classes"], embedding_dim=config["embedding_dim"]).to(device)
        model.load_state_dict(torch.load(weights_path, map_location=device))
        model.eval()
        return cls(model, config, device, build_reid_transform(config))

    @torch.no_grad()
    def embed(self, pil_image) -> list:
        x = self.transform(pil_image).unsqueeze(0).to(self.device)
        pooled, _, _ = self.model(x)
        embedding = F.normalize(pooled, dim=1)
        return embedding.cpu().numpy()[0].tolist()
