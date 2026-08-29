"""
VariSetu Backend — vision_adapter.py (real model version).

Drop-in replacement for Backend/app/integrations/vision_adapter.py. Same
method names/shapes the rest of the backend already calls (crowd.py,
lost_persons.py, medical.py etc. don't need to change), but now backed by
the deployed HF Space instead of hardcoded DEMO data.

Add to Backend/requirements.txt:
    gradio_client>=1.3.0

Add to Backend/.env / config.py:
    HF_SPACE_ID=your-hf-username/varisetu-demo
    VISION_PROVIDER=hf_space          # instead of "mock"
"""

import io
import logging
import random
from typing import Any, Dict, List, Optional

try:
    from gradio_client import Client, handle_file
except ImportError:
    Client = None
    handle_file = None

from app.core.config import settings

logger = logging.getLogger("varisetu.vision")


class VisionAdapter:
    """
    Vision processing interface for crowd density, fall detection, and
    face/person matching — now calling the deployed VariSetu HF Space.
    """

    def __init__(self):
        self.provider = settings.VISION_PROVIDER
        self._client: Optional[Any] = None
        if self.provider == "hf_space":
            if Client is None:
                logger.warning("gradio_client is not installed; operating in fallback mock mode.")
                self.provider = "mock"
            else:
                try:
                    self._client = Client(settings.HF_SPACE_ID)
                except Exception as e:
                    logger.warning("Failed to initialize HF Space Client (%s); fallback to mock.", e)
                    self.provider = "mock"

    # -------------------------------------------------------------------
    # Crowd density
    # -------------------------------------------------------------------
    async def estimate_crowd(self, camera_id: str, frame_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Estimate crowd density from a CCTV frame.
        """
        if self.provider != "hf_space" or frame_bytes is None or not self._client:
            simulated_data = {
                "CAM-12": {"density": 88.0, "count": 1420, "trend": "RISING", "risk": "HIGH"},
                "CAM-04": {"density": 94.0, "count": 2850, "trend": "RISING", "risk": "CRITICAL"},
                "CAM-08": {"density": 62.0, "count": 890, "trend": "EASING", "risk": "MODERATE"},
                "CAM-01": {"density": 35.0, "count": 410, "trend": "STABLE", "risk": "LOW"},
            }
            fallback = {"density": random.uniform(40.0, 75.0), "count": random.randint(500, 1200), "trend": "STABLE", "risk": "MODERATE"}
            info = simulated_data.get(camera_id, fallback)
            return {
                "camera_id": camera_id,
                "density_percentage": info["density"],
                "people_count": info["count"],
                "trend": info["trend"],
                "risk_level": info["risk"],
                "source": "DEMO",
            }

        result = self._client.predict(
            handle_file(io.BytesIO(frame_bytes)),
            api_name="/crowd_density",
        )
        return {
            "camera_id": camera_id,
            "people_count": result.get("estimated_count"),
            "density_level": result.get("density_level"),
            "source": "CSRNET",
        }

    # -------------------------------------------------------------------
    # Fall detection
    # -------------------------------------------------------------------
    async def detect_fall(self, camera_id: str, clip_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Run fall detection on a short clip of one tracked person.
        """
        if self.provider != "hf_space" or clip_path is None or not self._client:
            return {"detected": True, "camera_id": camera_id, "confidence": 0.92, "bounding_box": [120, 340, 210, 480], "source": "DEMO"}

        result = self._client.predict(
            handle_file(clip_path),
            api_name="/fall_detection",
        )
        return {
            "detected": result.get("fall_detected", False),
            "camera_id": camera_id,
            "confidence": result.get("max_fall_probability"),
            "source": "FALL_MODEL",
        }

    # -------------------------------------------------------------------
    # Face / person embeddings
    # -------------------------------------------------------------------
    async def generate_face_embedding(self, photo_bytes: bytes) -> List[float]:
        """Generate facial feature embedding vector."""
        if self.provider == "hf_space":
            raise NotImplementedError(
                "Use search_face_in_stream() for face matching; this Space exposes "
                "pairwise comparison endpoints, not a standalone embedding export."
            )
        random.seed(len(photo_bytes) if photo_bytes else 42)
        return [random.uniform(-1.0, 1.0) for _ in range(128)]

    async def search_face_in_stream(
        self, query_photo_bytes: bytes, candidate_photos: List[bytes]
    ) -> List[Dict[str, Any]]:
        """
        Compares a query photo (from the Lost & Found report) against a list
        of candidate CCTV-crop photos, using BOTH the Person Re-ID model
        (primary) and the Face Recognition model (secondary confirmation),
        matching the report's stated design: Re-ID is never gated by face
        matching, only confirmed/challenged by it.
        """
        if self.provider != "hf_space":
            return [{
                "camera_code": "CAM-04", "similarity_score": 0.89,
                "confidence": 0.94, "source": "DEMO",
            }]

        results = []
        for i, candidate_bytes in enumerate(candidate_photos):
            reid_result = self._client.predict(
                handle_file(io.BytesIO(query_photo_bytes)),
                handle_file(io.BytesIO(candidate_bytes)),
                api_name="/person_reid",
            )
            face_result = self._client.predict(
                handle_file(io.BytesIO(query_photo_bytes)),
                handle_file(io.BytesIO(candidate_bytes)),
                api_name="/face_recognition",
            )
            results.append({
                "candidate_index": i,
                "reid_similarity": reid_result.get("similarity"),
                "reid_confidence": reid_result.get("confidence_label"),
                "face_similarity": face_result.get("similarity"),
                "face_is_match": face_result.get("is_match"),
                "source": "REID_MODEL+FACE_MODEL",
            })

        results.sort(key=lambda r: r["reid_similarity"] or -1, reverse=True)
        return results


vision_adapter = VisionAdapter()
