"""
VariSetu - Person Re-ID preprocessing.

Decoupled from the training notebook on purpose: the backend must never import
notebook code, and this file is the single source of truth for how a raw
image is turned into model input, both at training time and at inference time.
"""

from PIL import Image
from torchvision import transforms as T


def build_eval_transform(config: dict) -> T.Compose:
    """
    Build the exact (non-augmented) preprocessing pipeline used at inference time.
    `config` is the loaded model_config.json dict -- nothing here is hard-coded,
    so if the model is retrained with a different image size / normalization,
    this file does not need to change.
    """
    height = config["img_size"]["height"]
    width = config["img_size"]["width"]
    mean = config["normalize_mean"]
    std = config["normalize_std"]

    return T.Compose([
        T.Resize((height, width)),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])


def load_and_validate_image(image_path_or_bytes) -> Image.Image:
    """
    Load an image from a filesystem path, file-like object, or raw bytes, and
    validate it before it reaches the model. Raises ValueError with a clear
    message on anything malformed -- the backend should catch this and return
    a 4xx error to the caller rather than letting a bad crop reach the model.
    """
    try:
        img = Image.open(image_path_or_bytes)
        img = img.convert("RGB")
    except Exception as e:
        raise ValueError(f"Could not read image: {e}")

    width, height = img.size
    if width < 20 or height < 40:
        # A person crop smaller than this is almost certainly a bad detection
        # (e.g. a hand, a partial object) rather than a usable person image.
        raise ValueError(
            f"Image too small to be a valid person crop ({width}x{height}px). "
            "Check the upstream person-detection step."
        )

    return img
