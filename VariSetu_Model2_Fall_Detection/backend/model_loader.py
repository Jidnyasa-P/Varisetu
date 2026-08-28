"""
VariSetu — Model 2 (Fall/Medical-Distress Detection) — model_loader.py

Loads fall_model.pt + model_config.json once at process startup. Mirrors the
loading convention used for the Person Re-ID model (model_loader / artifacts_dir
pattern) so both models can be wired into the backend the same way.
"""

import json
import os

import torch
import torch.nn as nn


class AttentionPool(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.Linear(dim, 1)

    def forward(self, x):  # x: [B, T, dim]
        w = torch.softmax(self.attn(x).squeeze(-1), dim=1)
        return torch.bmm(w.unsqueeze(1), x).squeeze(1), w


class FallDetectionModel(nn.Module):
    """MUST match the architecture in train_fall_detection_colab.py exactly —
    this is a plain nn.Module (not TorchScript), so the class definition here is
    what actually gets populated by load_state_dict."""

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
    """Everything the inference engine needs, loaded once."""

    def __init__(self, model: nn.Module, config: dict, device: torch.device):
        self.model = model
        self.config = config
        self.device = device
        self.window_size = config["input_window_frames"]
        self.stride = config["input_stride_frames"]
        self.feat_dim = config["feature_dim_per_frame"]
        self.feature_mean = config["feature_mean"]
        self.feature_std = config["feature_std"]
        self.threshold = config["recommended_binary_threshold"]


def load_fall_model(artifacts_dir: str, device: str = "cpu") -> FallModelBundle:
    """
    Required files in `artifacts_dir`:
      - fall_model.pt      (from Section 8 of the Colab training script)
      - model_config.json  (from Section 8 of the Colab training script)

    Raises FileNotFoundError immediately (fail fast at startup) if either is
    missing, per the same contract used for the Re-ID model.
    """
    model_path = os.path.join(artifacts_dir, "fall_model.pt")
    config_path = os.path.join(artifacts_dir, "model_config.json")

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"fall_model.pt not found at {model_path}")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"model_config.json not found at {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    torch_device = torch.device(device)
    checkpoint = torch.load(model_path, map_location=torch_device)

    model = FallDetectionModel(feat_dim=config["feature_dim_per_frame"],
                                hidden=config.get("hidden_size", 128),
                                num_layers=config.get("num_lstm_layers", 2))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(torch_device)
    model.eval()

    return FallModelBundle(model=model, config=config, device=torch_device)
