# MODEL_API_CONTRACT.md — Person Re-Identification (Missing-Person Appearance Matching)

This document describes the interface between the Re-ID model component and the backend.
It covers **one** of the three VariSetu ML components (Person Re-ID). The other two
(Crowd Density, Fall/Medical-Distress Detection) will each get their own contract section
once those notebooks are built.

---

## 1. Loading the model (once, at backend startup)

```python
from model.inference import ReIDInferenceEngine

reid_engine = ReIDInferenceEngine(artifacts_dir="model/artifacts")  # load ONCE, reuse across requests
```

Required files in `model/artifacts/`:
- `reid_model.pt` — trained weights (from the Colab notebook export)
- `model_config.json` — preprocessing config, thresholds, label mapping (from the Colab notebook export)

Do not reload the model per-request — instantiate `ReIDInferenceEngine` once (e.g. in a FastAPI
`lifespan` handler or a module-level singleton) and reuse it.

---

## 2. Endpoint A — Embed a query image (new missing-person report)

**Purpose:** called when a Lost & Found case is registered (voice call → transcript → "last seen"
photo or matched CCTV frame), to produce the embedding used for searching.

**Input**
| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | binary (JPEG/PNG) | yes | A cropped person image. Full video frames should be cropped to the person bounding box upstream (by the detection stage), not sent whole. |

**Preprocessing requirements:** none required from the caller — resizing/normalization is handled
internally. Minimum usable crop size: 20×40px; smaller images are rejected (see Error Conditions).

**Output**
```json
{
  "embedding": [0.0123, -0.0456, "...", 0.0891],
  "embedding_dim": 2048
}
```

---

## 3. Endpoint B — Rank candidates (search a gallery of camera-crop embeddings)

**Purpose:** given a query embedding, return the top-K most likely matches from recent
camera-detection embeddings for control-room review.

**Input**
| Field | Type | Required | Notes |
|---|---|---|---|
| `query_embedding` | array[float], length 2048 | yes | From Endpoint A |
| `gallery` | array of objects | yes | Each: `{"id": str, "embedding": array[float], ...any metadata}`. In production this should come from a Qdrant nearest-neighbour query, not a full table scan — see `inference.py` note. |
| `top_k` | int | no (default 10) | Max candidates to return |

**Output**
```json
{
  "matches": [
    {
      "gallery_id": "cam04_track_88231",
      "similarity": 0.8123,
      "confidence_label": "high",
      "metadata": {"camera_id": "CAM-04", "timestamp": "2026-08-26T14:03:11Z", "location": "Pandharpur Chowk"}
    }
  ]
}
```

| Output field | Type | Range | Meaning |
|---|---|---|---|
| `similarity` | float | -1.0 to 1.0 | Cosine similarity between query and candidate embedding. Higher = more likely same person. |
| `confidence_label` | string | `"high"` / `"medium"` / `"low"` / `"unknown"` | Derived from the verification threshold established during training (Section 19 of the notebook), **not** an arbitrary cutoff. |

**Critical constraint:** this endpoint returns **candidates for human confirmation only.**
Per the project report's own risk mitigation, no `similarity` or `confidence_label` value should
ever trigger an automatic dispatch or public announcement — the dashboard must always route this
through a control-room officer's confirmation step before any action is taken.

---

## 4. Endpoint C — Verify a pair (direct same/different check)

**Purpose:** when a control-room officer has two specific images (e.g. a family-provided photo and
one CCTV frame) and wants a direct same-person check rather than a ranked search.

**Input**
| Field | Type | Required |
|---|---|---|
| `image_a` | binary | yes |
| `image_b` | binary | yes |

**Output**
```json
{
  "same_person_predicted": true,
  "similarity": 0.79,
  "confidence_label": "high",
  "threshold_used": 0.62
}
```

---

## 5. Error conditions

| Condition | Response |
|---|---|
| Image unreadable / corrupt | HTTP 400, `{"error": "Could not read image: <detail>"}` |
| Image smaller than 20×40px | HTTP 400, `{"error": "Image too small to be a valid person crop (...)"}` |
| Empty `gallery` in Endpoint B | Returns `{"matches": []}`, HTTP 200 (not an error — a genuinely empty search space) |
| Model/artifact files missing at startup | Fails fast at startup with `FileNotFoundError`, not at request time |

---

## 6. Example end-to-end request/response (Endpoint B)

**Request**
```json
POST /api/reid/rank-candidates
{
  "query_embedding": ["...2048 floats..."],
  "gallery": [
    {"id": "cam04_track_88231", "embedding": ["...2048 floats..."], "camera_id": "CAM-04", "timestamp": "2026-08-26T14:03:11Z"},
    {"id": "cam12_track_10042", "embedding": ["...2048 floats..."], "camera_id": "CAM-12", "timestamp": "2026-08-26T14:04:02Z"}
  ],
  "top_k": 5
}
```

**Response**
```json
{
  "matches": [
    {"gallery_id": "cam04_track_88231", "similarity": 0.8123, "confidence_label": "high",
     "metadata": {"camera_id": "CAM-04", "timestamp": "2026-08-26T14:03:11Z"}},
    {"gallery_id": "cam12_track_10042", "similarity": 0.4310, "confidence_label": "low",
     "metadata": {"camera_id": "CAM-12", "timestamp": "2026-08-26T14:04:02Z"}}
  ]
}
```

---

## 7. Deployment requirements

- **Python:** 3.10+
- **Dependencies:** see `requirements.txt` (torch, torchvision, numpy, Pillow; FastAPI/Qdrant optional depending on backend stack)
- **Compute:** GPU not required for inference (unlike training) — a single embedding takes well under
  100ms on CPU for this model size; GPU helps mainly for batch embedding of many camera crops at once.
- **Model size:** ResNet50-based, ~25M parameters (~100MB checkpoint file)
- **Storage:** the two artifact files (`reid_model.pt`, `model_config.json`) need to be available to the
  backend process — via a mounted volume, cloud storage bucket, or bundled into the deployment image.
- **Known limitation carried into deployment:** this model is trained on Market-1501, not Wari-corridor
  footage — see the notebook's Limitations section. Flag this to whoever deploys it; expect a
  fine-tuning pass before any real-event use.
