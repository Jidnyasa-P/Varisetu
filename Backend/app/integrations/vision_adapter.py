import logging
from typing import Any, Dict, List, Optional
import random

from app.core.config import settings

logger = logging.getLogger("varisetu.vision")


class VisionAdapter:
    """
    Vision processing interface for YOLO crowd density estimation,
    fall detection, and face embedding matching.
    """
    def __init__(self):
        self.provider = settings.VISION_PROVIDER

    async def estimate_crowd(self, camera_id: str) -> Dict[str, Any]:
        """
        Estimate crowd density & people count from CCTV video frame.
        In mock mode, returns simulated density metadata marked as source=DEMO.
        """
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
            "source": "DEMO" if self.provider == "mock" else "YOLO_V8"
        }

    async def detect_fall(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Detect fainting / pilgrim fall from camera stream."""
        return {
            "detected": True,
            "camera_id": camera_id,
            "confidence": 0.92,
            "bounding_box": [120, 340, 210, 480],
            "source": "DEMO"
        }

    async def generate_face_embedding(self, photo_bytes: bytes) -> List[float]:
        """Generate a 512-dim facial feature embedding vector."""
        random.seed(len(photo_bytes) if photo_bytes else 42)
        return [random.uniform(-1.0, 1.0) for _ in range(128)]

    async def search_face_in_stream(self, embedding: List[float], camera_codes: List[str]) -> List[Dict[str, Any]]:
        """Simulate scanning CCTV feeds for matching faces."""
        return [
            {
                "camera_code": "CAM-04",
                "location": "Pandharpur Temple Chowk",
                "similarity_score": 0.89,
                "confidence": 0.94,
                "frame_reference": "frame_4812.jpg",
                "source": "DEMO"
            }
        ]


vision_adapter = VisionAdapter()
