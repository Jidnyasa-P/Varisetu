"""
VariSetu - Crowd Density Estimation standalone inference.

Flow: Raw Input -> Validation -> Preprocessing -> Model -> Prediction -> Post-processing -> Structured Output

This is the ONLY file the backend needs to import for crowd-density
functionality. It never gets copied-and-pasted from the notebook -- it wraps
model_loader.py and preprocessing.py and returns plain dicts, ready to
serialize to JSON. Mirrors the shape of the Re-ID component's inference.py
for consistency across the two ML components.
"""

from dataclasses import dataclass
from typing import List, Optional

from preprocessing import load_and_validate_image
from model_loader import CrowdDensityModelBundle


# Density thresholds (people per square metre of *visible frame area*, not
# per full camera coverage). Values below are the standard bands used in
# pedestrian-safety literature (e.g. Fruin's Level-of-Service classes,
# simplified to three bands for the dashboard). These are exposed in
# model_config.json (not hard-coded) so the control room can retune them
# per choke-point without a redeploy.
@dataclass
class CrowdAlert:
    estimated_count: float
    density_level: str          # "normal" / "moderate" / "critical", per report's Fig.12.1 UI
    frame_area_label: Optional[str] = None   # e.g. "CAM-04" passed through by the caller


class CrowdDensityInferenceEngine:
    """
    Load once (e.g. at FastAPI startup via a dependency / lifespan event),
    reuse across every request.

    Example:
        engine = CrowdDensityInferenceEngine(artifacts_dir="model/artifacts")
        result = engine.estimate(frame_bytes, camera_id="CAM-04")
    """

    def __init__(self, artifacts_dir: str = "model/artifacts", device: str = None):
        self.bundle = CrowdDensityModelBundle.load(artifacts_dir, device=device)
        self.thresholds = self.bundle.config.get(
            "density_alert_thresholds",
            {"moderate_count": 150, "critical_count": 400},
        )

    def _density_level(self, count: float) -> str:
        if count >= self.thresholds["critical_count"]:
            return "critical"
        if count >= self.thresholds["moderate_count"]:
            return "moderate"
        return "normal"

    def estimate(self, image_path_or_bytes, camera_id: Optional[str] = None) -> dict:
        """
        Full pipeline for one CCTV frame: validate -> preprocess -> model ->
        count -> alert level -> structured output. Raises ValueError on
        invalid input (backend should catch and return HTTP 400).

        Returns:
            {
              "estimated_count": 187.4,
              "density_level": "moderate",
              "camera_id": "CAM-04",
              "density_map_shape": [270, 480]   # for overlay rendering on the dashboard
            }
        """
        img = load_and_validate_image(image_path_or_bytes)
        density_map, count = self.bundle.predict(img)

        return {
            "estimated_count": round(count, 1),
            "density_level": self._density_level(count),
            "camera_id": camera_id,
            "density_map_shape": list(density_map.shape),
        }

    def estimate_with_heatmap(self, image_path_or_bytes, camera_id: Optional[str] = None) -> dict:
        """
        Same as estimate(), but also returns the raw density map as a nested
        list (JSON-serializable) for the dashboard's live heatmap overlay
        (Fig.5.1 Layer 5, "Live Crowd Heatmap"). Heavier payload -- use
        estimate() instead for the polling/alerting path, and this only when
        a control-room operator opens a specific camera tile.
        """
        img = load_and_validate_image(image_path_or_bytes)
        density_map, count = self.bundle.predict(img)

        return {
            "estimated_count": round(count, 1),
            "density_level": self._density_level(count),
            "camera_id": camera_id,
            "density_map": density_map.round(4).tolist(),
        }

    def estimate_batch(self, images: List, camera_ids: Optional[List[str]] = None) -> List[dict]:
        """Convenience wrapper for scoring several camera tiles in one call (e.g. a dashboard refresh)."""
        camera_ids = camera_ids or [None] * len(images)
        return [self.estimate(img, cam_id) for img, cam_id in zip(images, camera_ids)]


# -----------------------------------------------------------------------------
# NOTE on scaling beyond a demo:
#
# estimate_batch() above loops one image at a time, which is fine for a
# hackathon demo (a handful of camera tiles on a dashboard refresh) but does
# not batch on the GPU. For the report's target of 14+ live CCTV feeds
# refreshing every few seconds, stack the preprocessed tensors and run one
# forward pass (see CrowdDensityModelBundle -- add a batched predict() the
# same way ReIDModelBundle.embed_batch() does it) rather than calling
# estimate() in a Python for-loop.
# -----------------------------------------------------------------------------
