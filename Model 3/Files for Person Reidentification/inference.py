"""
VariSetu - Person Re-ID standalone inference.

Flow: Raw Input -> Validation -> Preprocessing -> Model -> Prediction -> Post-processing -> Structured Output

This is the ONLY file the backend needs to import for Re-ID functionality.
It never gets copied-and-pasted from the notebook -- it wraps model_loader.py
and preprocessing.py and returns plain dicts/lists, ready to serialize to JSON.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from preprocessing import load_and_validate_image
from model_loader import ReIDModelBundle


@dataclass
class MatchCandidate:
    gallery_id: str            # e.g. a CCTV detection/track ID from your backend's DB
    similarity: float          # cosine similarity, range [-1, 1], higher = more likely same person
    confidence_label: str      # "high" / "medium" / "low", derived from the verification threshold
    metadata: dict = field(default_factory=dict)   # camera_id, timestamp, location, etc. passed through


class ReIDInferenceEngine:
    """
    Load once (e.g. at FastAPI startup via a dependency / lifespan event),
    reuse across every request.

    Example:
        engine = ReIDInferenceEngine(artifacts_dir="model/artifacts")

        # embedding a new "missing person" query crop:
        query_embedding = engine.embed_query(image_bytes)

        # ranking it against a gallery of recent camera-crop embeddings
        # (in production this gallery lookup should be a Qdrant / vector-DB
        # nearest-neighbour query, not a python loop -- see note at bottom of file)
        matches = engine.rank_candidates(query_embedding, gallery)
    """

    def __init__(self, artifacts_dir: str = "model/artifacts", device: str = None):
        self.bundle = ReIDModelBundle.load(artifacts_dir, device=device)
        # Pulled directly from training-time evaluation (Section 19 of the notebook) --
        # NOT invented here. If the model is retrained, this value updates automatically
        # because it's read from model_config.json, not hard-coded.
        self.verification_threshold = self.bundle.config.get("verification_threshold_at_5pct_fpr")

    def embed_query(self, image_path_or_bytes) -> List[float]:
        """
        Step 1-4 of the pipeline for a single input image: validate -> preprocess -> model -> embedding.
        Raises ValueError on invalid input (backend should catch and return HTTP 400).
        """
        img = load_and_validate_image(image_path_or_bytes)
        return self.bundle.embed(img)

    def embed_query_batch(self, images: List) -> List[List[float]]:
        """Same as embed_query but for a batch of images (e.g. all person-crops from one video frame)."""
        validated = [load_and_validate_image(img) for img in images]
        return self.bundle.embed_batch(validated)

    def _confidence_label(self, similarity: float) -> str:
        """
        Post-processing: turn a raw similarity score into a human-readable confidence
        band for the control-room dashboard, anchored to the trained verification
        threshold rather than an arbitrary cutoff.
        """
        if self.verification_threshold is None:
            return "unknown"
        if similarity >= self.verification_threshold:
            # comfortably above the ~5% false-positive-rate operating point
            margin = similarity - self.verification_threshold
            return "high" if margin >= 0.05 else "medium"
        return "low"

    def rank_candidates(
        self,
        query_embedding: List[float],
        gallery: List[dict],
        top_k: int = 10,
    ) -> List[MatchCandidate]:
        """
        Step 5-6 of the pipeline: prediction -> post-processing -> structured output.

        `gallery` is a list of dicts, each with at minimum:
            {"id": <str>, "embedding": <List[float]>, ...any other metadata to pass through...}

        Returns the top_k candidates sorted by similarity, descending, as MatchCandidate
        objects -- NEVER an auto-confirmed match. The control-room UI must always show
        these as candidates requiring human confirmation, per the report's own risk
        mitigation ("a control-room officer always confirms a match before dispatch").
        """
        import numpy as np

        if not gallery:
            return []

        q = np.array(query_embedding)
        sims = []
        for entry in gallery:
            g = np.array(entry["embedding"])
            sim = float(np.dot(q, g))  # both vectors are already L2-normalized -> dot product = cosine similarity
            sims.append(sim)

        order = np.argsort(sims)[::-1][:top_k]
        results = []
        for i in order:
            entry = gallery[i]
            sim = sims[i]
            results.append(MatchCandidate(
                gallery_id=entry["id"],
                similarity=round(sim, 4),
                confidence_label=self._confidence_label(sim),
                metadata={k: v for k, v in entry.items() if k not in ("id", "embedding")},
            ))
        return results

    def verify_pair(self, image_a, image_b) -> dict:
        """
        Direct same-person / different-person check between two images (the
        "verification" framing evaluated in Section 19 of the notebook).
        Returns a structured dict, not just a bool, so the frontend can show the
        similarity score alongside the yes/no.
        """
        emb_a = self.embed_query(image_a)
        emb_b = self.embed_query(image_b)
        import numpy as np
        sim = float(np.dot(np.array(emb_a), np.array(emb_b)))
        return {
            "same_person_predicted": sim >= (self.verification_threshold or 0.5),
            "similarity": round(sim, 4),
            "confidence_label": self._confidence_label(sim),
            "threshold_used": self.verification_threshold,
        }


# -----------------------------------------------------------------------------
# NOTE on scaling the gallery lookup beyond a demo:
#
# `rank_candidates` above does an in-memory linear scan, which is fine for a
# hackathon demo (hundreds of candidate crops) but will not scale to a real
# 250 km, multi-day corridor with thousands of camera detections per minute.
# Your original report already specifies Qdrant for this reason -- in
# production, `gallery` should be replaced with a Qdrant nearest-neighbour
# query (upsert each new camera-crop embedding as it's produced, query with
# the missing-person's query embedding, get back the top_k with scores
# directly from Qdrant instead of scanning in Python).
# -----------------------------------------------------------------------------
