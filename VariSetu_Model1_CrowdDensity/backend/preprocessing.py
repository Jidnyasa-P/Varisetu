"""
VariSetu - Crowd Density Estimation preprocessing.

Decoupled from the training notebook on purpose: the backend must never
import notebook code, and this file is the single source of truth for how a
raw CCTV frame is turned into model input, both at training time and at
inference time.

CSRNet is fully-convolutional, so it accepts any input size -- but the
frontend downsamples by exactly 8x (three 2x max-pools), so height and width
must each be a multiple of 8 or the backend's dilated convs and the final
upsample-for-overlay step will be off by a few pixels. This file enforces
that constraint in one place.
"""

from PIL import Image
from torchvision import transforms as T


def _round_down_to_multiple_of_8(value: int) -> int:
    return max(8, (value // 8) * 8)


def build_eval_transform(config: dict):
    """
    Build the exact (non-augmented) preprocessing pipeline used at inference
    time. `config` is the loaded model_config.json dict -- nothing here is
    hard-coded, so if the model is retrained with a different cap size /
    normalization, this file does not need to change.

    Unlike a fixed-size classifier transform, this returns a *function*
    (image -> (tensor, original_size)) rather than a plain T.Compose, because
    the resize target depends on each image's own aspect ratio (we cap the
    longer side, we don't force a square).
    """
    max_dim = config["preprocessing"]["max_dimension"]
    mean = config["preprocessing"]["normalize_mean"]
    std = config["preprocessing"]["normalize_std"]

    normalize = T.Compose([T.ToTensor(), T.Normalize(mean, std)])

    def transform(pil_image: Image.Image):
        orig_size = pil_image.size  # (W, H), kept so the caller can upsample the density map back
        w, h = orig_size

        # Cap the longer side at max_dimension (CCTV frames and UCF-QNRF
        # source images range from a few hundred px to 6000+ px on a side;
        # running the full-resolution frame through a VGG frontend is both
        # unnecessary for crowd-density accuracy and too slow/memory-heavy
        # for real-time dashboard use).
        scale = min(1.0, max_dim / max(w, h))
        new_w, new_h = int(w * scale), int(h * scale)

        new_w = _round_down_to_multiple_of_8(new_w)
        new_h = _round_down_to_multiple_of_8(new_h)

        resized = pil_image.resize((new_w, new_h), Image.BILINEAR)
        tensor = normalize(resized)
        return tensor, orig_size

    return transform


def load_and_validate_image(image_path_or_bytes) -> Image.Image:
    """
    Load an image from a filesystem path, file-like object, or raw bytes,
    and validate it before it reaches the model. Raises ValueError with a
    clear message on anything malformed -- the backend should catch this and
    return a 4xx error to the caller rather than letting a bad frame reach
    the model.
    """
    try:
        img = Image.open(image_path_or_bytes)
        img = img.convert("RGB")
    except Exception as e:
        raise ValueError(f"Could not read image: {e}")

    width, height = img.size
    if width < 64 or height < 64:
        # Below this, a CCTV tile is almost certainly a bad crop/thumbnail,
        # not a usable crowd-scene frame.
        raise ValueError(
            f"Image too small to be a valid crowd-scene frame ({width}x{height}px). "
            "Check the upstream frame-capture step."
        )

    return img
