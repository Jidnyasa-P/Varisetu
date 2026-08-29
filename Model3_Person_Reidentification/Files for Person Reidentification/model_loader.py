"""
VariSetu - Person Re-ID model loader.

Loads the model ONCE (at backend startup), not per-request. Re-instantiating
and reloading a ResNet50 on every API call would make inference latency
unacceptable and waste GPU/CPU cycles.

Usage in a backend (e.g. FastAPI):

    from model.model_loader import ReIDModelBundle

    reid_bundle = ReIDModelBundle.load("model/artifacts")   # done once at app startup

    # per request:
    embedding = reid_bundle.embed(pil_image)
"""

import os
import json

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet50


class ReIDModel(nn.Module):
    """
    Must match the architecture trained in Varithon_Model_PersonReID.ipynb
    (ResNet50 backbone, stride-1 last stage, BNNeck) exactly, or the saved
    state_dict will fail to load / silently load incorrectly.
    """
    def __init__(self, num_classes: int, embedding_dim: int = 2048):
        super().__init__()
        backbone = resnet50(weights=None)  # weights loaded from our checkpoint, not ImageNet, at inference time
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


class ReIDModelBundle:
    """
    Wraps the model + config + preprocessing together so the backend has one
    object to hold onto, loaded once, thread-safe for read-only inference.
    """

    def __init__(self, model: ReIDModel, config: dict, device: torch.device, transform):
        self.model = model
        self.config = config
        self.device = device
        self.transform = transform

    @classmethod
    def load(cls, artifacts_dir: str, device: str = None):
        device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        config_path = os.path.join(artifacts_dir, "model_config.json")
        weights_path = os.path.join(artifacts_dir, "reid_model.pt")

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"model_config.json not found at {config_path}. "
                "Copy the file exported from the Colab notebook into this artifacts directory."
            )
        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"reid_model.pt not found at {weights_path}. "
                "Copy the file exported from the Colab notebook into this artifacts directory."
            )

        with open(config_path) as f:
            config = json.load(f)

        model = ReIDModel(
            num_classes=config["num_train_classes"],
            embedding_dim=config["embedding_dim"],
        ).to(device)
        model.load_state_dict(torch.load(weights_path, map_location=device))
        model.eval()

        # Imported here (not at module top) to avoid a hard circular-import
        # dependency between model_loader.py and preprocessing.py at import time.
        from preprocessing import build_eval_transform
        transform = build_eval_transform(config)

        return cls(model=model, config=config, device=device, transform=transform)

    @torch.no_grad()
    def embed(self, pil_image) -> "list[float]":
        """
        Turn a single PIL image (already validated/cropped to a person) into
        an L2-normalized embedding vector, as a plain Python list (JSON-serializable,
        ready to store in Postgres/Qdrant or return over an API).
        """
        x = self.transform(pil_image).unsqueeze(0).to(self.device)
        pooled, _, _ = self.model(x)
        embedding = F.normalize(pooled, dim=1)
        return embedding.cpu().numpy()[0].tolist()

    @torch.no_grad()
    def embed_batch(self, pil_images: list) -> "list[list[float]]":
        """Batched version for embedding many crops at once (e.g. all detections in one frame)."""
        tensors = torch.stack([self.transform(img) for img in pil_images]).to(self.device)
        pooled, _, _ = self.model(tensors)
        embeddings = F.normalize(pooled, dim=1)
        return embeddings.cpu().numpy().tolist()
