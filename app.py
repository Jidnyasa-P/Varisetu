"""
VariSetu - ML inference API server.

Wraps the existing model/ package (inference.py, model_loader.py,
preprocessing.py, face_confirmation.py) as HTTP endpoints, matching
MODEL_API_CONTRACT_REID.md. This is the ONE file that changes if you move
hosting platforms -- everything it imports is already platform-independent.

Run locally:      uvicorn app:app --host 0.0.0.0 --port 8000
Run in container:  see Dockerfile (Cloud Run injects $PORT automatically)
"""

import io
import os
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PIL import Image

from inference import ReIDInferenceEngine, LostAndFoundEngine

app = FastAPI(title="VariSetu ML Inference API")

# Loaded ONCE at process startup, reused across every request -- never re-instantiated per-request.
ARTIFACTS_DIR = os.environ.get("REID_ARTIFACTS_DIR", "artifacts")
ENABLE_FACE = os.environ.get("ENABLE_FACE_CONFIRMATION", "true").lower() == "true"

engine: Optional[LostAndFoundEngine] = None


@app.on_event("startup")
def load_models():
    global engine
    engine = LostAndFoundEngine(
        reid_artifacts_dir=ARTIFACTS_DIR,
        enable_face_confirmation=ENABLE_FACE,
    )
    print("Models loaded. Face confirmation enabled:", engine.face_engine is not None)


# -----------------------------------------------------------------------------
# Health check -- Cloud Run (and any platform) uses this to know the container
# is actually ready to serve traffic, not just that the process started.
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": engine is not None}


# -----------------------------------------------------------------------------
# Request/response schemas
# -----------------------------------------------------------------------------
class GalleryEntry(BaseModel):
    id: str
    embedding: List[float]
    metadata: dict = {}


class RankCandidatesRequest(BaseModel):
    query_embedding: List[float]
    gallery: List[GalleryEntry]
    top_k: int = 10


class MatchCandidateResponse(BaseModel):
    gallery_id: str
    similarity: float
    confidence_label: str
    metadata: dict = {}


# -----------------------------------------------------------------------------
# Endpoint A: embed a query image
# -----------------------------------------------------------------------------
@app.post("/reid/embed-query")
async def embed_query(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        embedding = engine.reid_engine.embed_query(io.BytesIO(image_bytes))
        return {"embedding": embedding, "embedding_dim": len(embedding)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# Endpoint B: rank candidates from a pre-embedded gallery (Re-ID only, no face)
# -----------------------------------------------------------------------------
@app.post("/reid/rank-candidates", response_model=List[MatchCandidateResponse])
async def rank_candidates(req: RankCandidatesRequest):
    gallery = [{"id": g.id, "embedding": g.embedding, **g.metadata} for g in req.gallery]
    matches = engine.reid_engine.rank_candidates(req.query_embedding, gallery, top_k=req.top_k)
    return [
        MatchCandidateResponse(
            gallery_id=m.gallery_id, similarity=m.similarity,
            confidence_label=m.confidence_label, metadata=m.metadata,
        )
        for m in matches
    ]


# -----------------------------------------------------------------------------
# Endpoint C: verify a pair directly (Re-ID)
# -----------------------------------------------------------------------------
@app.post("/reid/verify-pair")
async def verify_pair_reid(image_a: UploadFile = File(...), image_b: UploadFile = File(...)):
    try:
        bytes_a, bytes_b = await image_a.read(), await image_b.read()
        emb_a = engine.reid_engine.embed_query(io.BytesIO(bytes_a))
        emb_b = engine.reid_engine.embed_query(io.BytesIO(bytes_b))
        import numpy as np
        sim = float(np.dot(np.array(emb_a), np.array(emb_b)))
        threshold = engine.reid_engine.verification_threshold or 0.5
        return {"same_person_predicted": sim >= threshold, "similarity": round(sim, 4), "threshold_used": threshold}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# Endpoint D: full Lost & Found search -- Re-ID primary + face secondary confirmation.
# This is the endpoint the backend calls for an actual missing-person search.
# Gallery entries may optionally include a base64 face_crop for face confirmation.
# -----------------------------------------------------------------------------
class LostFoundGalleryEntry(BaseModel):
    id: str
    embedding: List[float]
    face_crop_base64: Optional[str] = None
    metadata: dict = {}


class LostFoundSearchRequest(BaseModel):
    gallery: List[LostFoundGalleryEntry]
    top_k: int = 10


@app.post("/lostfound/search", response_model=List[MatchCandidateResponse])
async def lostfound_search(
    gallery_json: str,   # sent as a form field since this endpoint also takes a file upload
    query_image: UploadFile = File(...),
):
    import json, base64
    try:
        parsed = LostFoundSearchRequest(**json.loads(gallery_json))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid gallery_json: {e}")

    query_bytes = await query_image.read()

    gallery = []
    for entry in parsed.gallery:
        item = {"id": entry.id, "embedding": entry.embedding, **entry.metadata}
        if entry.face_crop_base64:
            item["face_crop"] = Image.open(io.BytesIO(base64.b64decode(entry.face_crop_base64)))
        gallery.append(item)

    try:
        matches = engine.search(io.BytesIO(query_bytes), gallery, top_k=parsed.top_k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return [
        MatchCandidateResponse(
            gallery_id=m.gallery_id, similarity=m.similarity,
            confidence_label=m.combined_confidence_label or m.confidence_label,
            metadata={**m.metadata, "face_available": m.face_available, "face_similarity": m.face_similarity},
        )
        for m in matches
    ]
