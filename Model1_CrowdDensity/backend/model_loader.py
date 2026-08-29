"""
VariSetu - Crowd Density Estimation model loader.

Loads the model ONCE (at backend startup), not per-request. Mirrors the
loading pattern used by model_loader.py in the Person Re-ID component so the
two components stay consistent for whoever wires up the FastAPI backend.

Usage in a backend (e.g. FastAPI):

    from model.model_loader import CrowdDensityModelBundle

    density_bundle = CrowdDensityModelBundle.load("model/artifacts")  # once, at app startup

    # per request:
    density_map, count = density_bundle.predict(pil_image)
"""

import os
import json

import torch
import torch.nn as nn
from torchvision.models import vgg16_bn


class CSRNet(nn.Module):
    """
    CSRNet (Li, Zhang & Chen, CVPR 2018): VGG16 (first 10 conv layers, up to
    conv4_3) as a fixed-stride frontend feature extractor, followed by a
    dilated-convolution backend that grows receptive field without further
    downsampling. Output is a single-channel density map at 1/8 the input
    resolution; the predicted head-count is the sum over that map.

    Must match the architecture trained in
    Varithon_Model1_CrowdDensity.ipynb exactly, or the saved state_dict will
    fail to load / silently load incorrectly.
    """

    def __init__(self, load_imagenet_weights: bool = False):
        super().__init__()
        frontend_cfg = [64, 64, "M", 128, 128, "M", 256, 256, 256, "M", 512, 512, 512]
        backend_cfg = [512, 512, 512, 256, 128, 64]

        self.frontend = self._make_layers(frontend_cfg, in_channels=3)
        self.backend = self._make_layers(backend_cfg, in_channels=512, dilation=2)
        self.output_layer = nn.Conv2d(64, 1, kernel_size=1)

        if load_imagenet_weights:
            # Only used at training time to warm-start the frontend from
            # ImageNet-pretrained VGG16-BN. At inference time this is always
            # False -- weights come entirely from the checkpoint.
            vgg = vgg16_bn(weights="IMAGENET1K_V1")
            self._load_vgg_frontend(vgg)

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

    def _load_vgg_frontend(self, vgg):
        # Copy the first 33 layers of vgg16_bn (through conv4_3 + BN + ReLU,
        # excluding the 4th maxpool) into our frontend. Standard CSRNet
        # initialization; only exercised during training, never at inference.
        vgg_layers = list(vgg.features.children())
        own_layers = list(self.frontend.children())
        bn_frontend_len = 33  # conv1_1..conv4_3 with BatchNorm in vgg16_bn
        i = j = 0
        while i < len(own_layers) and j < bn_frontend_len:
            if isinstance(own_layers[i], nn.Conv2d) and isinstance(vgg_layers[j], nn.Conv2d):
                if own_layers[i].weight.shape == vgg_layers[j].weight.shape:
                    own_layers[i].weight.data = vgg_layers[j].weight.data.clone()
                    own_layers[i].bias.data = vgg_layers[j].bias.data.clone()
            i += 1
            j += 1

    def forward(self, x):
        x = self.frontend(x)
        x = self.backend(x)
        x = self.output_layer(x)
        return x


class CrowdDensityModelBundle:
    """
    Wraps the model + config + preprocessing together so the backend has one
    object to hold onto, loaded once, thread-safe for read-only inference.
    """

    def __init__(self, model: CSRNet, config: dict, device: torch.device, transform):
        self.model = model
        self.config = config
        self.device = device
        self.transform = transform

    @classmethod
    def load(cls, artifacts_dir: str, device: str = None):
        device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        config_path = os.path.join(artifacts_dir, "model_config.json")
        weights_path = os.path.join(artifacts_dir, "crowd_density_model.pt")

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"model_config.json not found at {config_path}. "
                "Copy the file exported from the Colab notebook into this artifacts directory."
            )
        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"crowd_density_model.pt not found at {weights_path}. "
                "Copy the file exported from the Colab notebook into this artifacts directory."
            )

        with open(config_path) as f:
            config = json.load(f)

        model = CSRNet(load_imagenet_weights=False).to(device)
        state_dict = torch.load(weights_path, map_location=device)
        model.load_state_dict(state_dict)
        model.eval()

        from preprocessing import build_eval_transform
        transform = build_eval_transform(config)

        return cls(model=model, config=config, device=device, transform=transform)

    @torch.no_grad()
    def predict(self, pil_image):
        """
        Run one image through the model and return (density_map, count).

        density_map: 2D numpy array, same relative layout as the input image
                      but at 1/8 resolution (upsampled back to input size
                      here for direct overlay on the dashboard's CCTV frame).
        count:        float, the estimated head-count (sum of the raw,
                      non-upsampled density map -- upsampling changes total
                      mass unless area-corrected, so counting always happens
                      on the raw model output, never the upsampled copy).
        """
        import torch.nn.functional as F
        import numpy as np

        x, orig_size = self.transform(pil_image)
        x = x.unsqueeze(0).to(self.device)

        raw_density = self.model(x)  # [1, 1, H/8, W/8]
        count = float(raw_density.sum().item())

        upsampled = F.interpolate(
            raw_density, size=(pil_image.size[1], pil_image.size[0]),
            mode="bilinear", align_corners=False,
        )
        density_map = upsampled.squeeze().cpu().numpy()

        return density_map, count

    @torch.no_grad()
    def predict_count_only(self, pil_image) -> float:
        """Cheaper path for callers (e.g. a live crowd-heatmap tile) that only need the number."""
        _, count = self.predict(pil_image)
        return count
