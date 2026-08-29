# MODEL_API_CONTRACT_FALL.md — Fall / Medical-Distress Detection

This document describes the interface between the Fall Detection model component
and the backend. It covers the **second** of the three VariSetu ML components
(Fall/Medical-Distress Detection). It follows the same structure as
`MODEL_API_CONTRACT_REID.md` for Person Re-ID so the two can be wired in
consistently.

---

## 1. Loading the model (once, at backend startup)

```python
from model.inference import FallDetectionInferenceEngine

fall_engine = FallDetectionInferenceEngine(artifacts_dir="model/artifacts", device="cpu")
# load ONCE, reuse across requests/tracks — do not re-instantiate per frame or per request
```

Required files in `model/artifacts/`:
- `fall_model.pt` — trained weights (from Section 8 of `train_fall_detection_colab.py`)
- `model_config.json` — feature layout, normalization stats, thresholds (same export step)

Fails fast at startup with `FileNotFoundError` if either file is missing — same
convention as the Re-ID model, so ops tooling can treat "missing artifact" the
same way for both.

---

## 2. Two integration modes

### Mode A — Live streaming (per CCTV track, frame-by-frame)

**Purpose:** called continuously from the video-ingestion / tracking layer
(Layer 2/3 in the architecture diagram) — one call per new frame per actively
tracked person.

```python
track_state = fall_engine.new_track_state()   # create when a new track (person) appears
# ... on every new frame for that track:
result = fall_engine.push_frame(track_state, cropped_person_frame_bgr)
# result is None on most calls (still accumulating frames); becomes a dict every
# `stride` frames (see model_config.json -> input_stride_frames) once the window fills
track_state.close()   # when the track ends (person leaves frame / lost)
```

**Input**
| Field | Type | Required | Notes |
|---|---|---|---|
| `cropped_person_frame_bgr` | np.ndarray (H, W, 3), OpenCV BGR | yes | Cropped to the one tracked person's bounding box, upstream of this call — same expectation as the Re-ID model's image input. Full wide-angle frames should not be passed directly. |

**Output (`result`, `None` until a window completes)**
```json
{
  "window_offset_frames": 135,
  "fall_probability": 0.87,
  "fall_detected": true,
  "threshold_used": 0.42,
  "stage": "fallen",
  "stage_probabilities": {"no_fall": 0.04, "falling": 0.09, "fallen": 0.87},
  "confidence_label": "high"
}
```

### Mode B — Batch / offline (a stored clip, e.g. re-scoring a flagged incident)

```python
report = fall_engine.classify_clip(list_of_cropped_person_frames_bgr)
```

**Output**
```json
{
  "windows": [ { ...same shape as Mode A result... }, ... ],
  "clip_verdict": {"fall_detected": true, "max_fall_probability": 0.91}
}
```

---

## 3. Output field reference

| Field | Type | Range | Meaning |
|---|---|---|---|
| `fall_probability` | float | 0.0–1.0 | Sigmoid output of the binary head. |
| `fall_detected` | bool | — | `fall_probability >= threshold_used`. `threshold_used` comes from training-time threshold selection (Section 7 of the training script — highest recall subject to fall-precision ≥ 0.60), **not** an arbitrary 0.5 cutoff. |
| `stage` | string | `no_fall` / `falling` / `fallen` | Richer context for the dashboard timeline; not separately threshold-tuned — treat as informative, not an alert trigger. |
| `confidence_label` | string | `high` / `medium` / `low` / `unknown` | Same three/four-tier convention as the Re-ID contract, scaled relative to this model's own threshold. |

**Critical constraint (same policy as Re-ID):** per the project report's Risk
& Mitigation section, `fall_detected = true` should surface as a **Medical Alert**
candidate on the command-centre dashboard for a control-room officer to confirm
and dispatch — it should not, by itself, auto-trigger ambulance dispatch or a
public announcement. This mirrors the Re-ID model's "candidates for human
confirmation only" rule and the report's own stated mitigation for false
positives on crowded, camera-only footage.

---

## 4. Error conditions

| Condition | Response |
|---|---|
| Model/artifact files missing at startup | Fails fast, `FileNotFoundError`, not at request time |
| Frame is not a valid image array | Raise `ValueError` from the caller before calling `push_frame` — this module assumes a valid decoded frame, matching the "crop upstream" contract |
| Pose detection fails on a given frame (occlusion, distant/tiny person) | Not an error — a zero-vector feature row is used for that frame (this matches training data, which also has detection dropouts); does not block the sliding window |
| A track is closed with fewer than `window_size` frames accumulated | No result is ever emitted for that track — this is expected for very short-lived tracks (e.g. someone briefly crossing a camera's edge) |

---

## 5. Deployment requirements

- **Python:** 3.10+
- **Dependencies:** see `requirements.txt` (torch, opencv-python-headless, mediapipe — uses MediaPipe's Tasks API (`PoseLandmarker`), which requires a one-time download of a small pretrained model asset, `pose_landmarker_lite.task`; `preprocessing.py`'s `ensure_pose_model_downloaded()` handles this automatically the first time `PoseFeatureExtractor` is constructed, or download it once at build time and place it at `model/artifacts/pose_landmarker_lite.task` for offline deployments; FastAPI/uvicorn optional depending on backend stack)
- **Compute:** GPU not required for inference — pose extraction + BiLSTM classification for one 45-frame window comfortably runs in well under real-time on CPU. GPU helps only if running many tracks' pose extraction in parallel at once.
- **Model size:** BiLSTM (2 layers, hidden=128) + attention pooling, well under 5M parameters (~small MB checkpoint) — much lighter than the Re-ID model.
- **Per-track state:** unlike Re-ID (stateless per image), this model IS stateful per track (`TrackState` holds the sliding window + the pose extractor's previous-frame values for velocity features). The backend must key `TrackState` instances by tracker ID and dispose of them when a track ends, or memory grows unbounded.
- **Known limitation carried into deployment:** trained on MCFD (staged, single-actor, indoor, 8 fixed cameras) — see the training script's `known_limitations` in `model_config.json`. Flag this to whoever deploys it; expect a fine-tuning/calibration pass on real Wari-corridor footage before any real-event use, exactly as noted for the Re-ID model.
