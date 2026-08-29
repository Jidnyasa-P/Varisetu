# MODEL_API_CONTRACT.md — Crowd Density Estimation

This document describes the interface between the Crowd Density model component
and the backend. It covers **one** of the three VariSetu ML components (Crowd
Density). It follows the same shape as `MODEL_API_CONTRACT_REID.md` so a backend
developer wiring up both components sees a consistent pattern.

---

## 1. Loading the model (once, at backend startup)

```python
from model.inference import CrowdDensityInferenceEngine

density_engine = CrowdDensityInferenceEngine(artifacts_dir="model/artifacts")  # load ONCE, reuse across requests
```

Required files in `model/artifacts/`:
- `crowd_density_model.pt` — trained weights (from the Colab notebook export)
- `model_config.json` — preprocessing config, alert thresholds, training metadata (from the Colab notebook export)

Do not reload the model per-request — instantiate `CrowdDensityInferenceEngine`
once (e.g. in a FastAPI `lifespan` handler or a module-level singleton) and
reuse it, exactly as with the Re-ID engine.

---

## 2. Endpoint A — Estimate crowd count for one frame

**Purpose:** called on a polling cadence per live CCTV feed (Fig.5.1 Layer 3,
"Crowd Density Estimation") to drive the choke-point heatmap and the
crush-risk alerting described in the report's Section 2 and Section 7.

**Input**
| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | binary (JPEG/PNG) | yes | A full CCTV frame (not a person crop — unlike Re-ID, this model needs the whole scene). |
| `camera_id` | string | no | Passed through untouched into the response for the caller's own bookkeeping. |

**Output**
```json
{
  "estimated_count": 187.4,
  "density_level": "moderate",
  "camera_id": "CAM-04",
  "density_map_shape": [270, 480]
}
```

| Output field | Type | Meaning |
|---|---|---|
| `estimated_count` | float | Estimated number of people visible in the frame. A float, not an int — this is a regression estimate (sum of a density map), not a discrete detection count, and rounding early would understate its uncertainty. |
| `density_level` | string | `"normal"` / `"moderate"` / `"critical"`, derived from `density_alert_thresholds` in `model_config.json` (tunable per choke-point, not hard-coded). |
| `density_map_shape` | [int, int] | Height/width of the underlying density map, for callers that want to fetch the full heatmap via Endpoint B and know its dimensions upfront. |

---

## 3. Endpoint B — Estimate with full heatmap (for dashboard overlay)

**Purpose:** called when a control-room operator opens a specific camera
tile and the dashboard needs to render the live crowd heatmap overlay
(Fig.5.1 Layer 5, "Live Crowd Heatmap"), not just the summary count.

**Input:** same as Endpoint A.

**Output**
```json
{
  "estimated_count": 187.4,
  "density_level": "moderate",
  "camera_id": "CAM-04",
  "density_map": [[0.001, 0.004, "..."], ["...", "..."]]
}
```

`density_map` is a 2-D array, same pixel dimensions as the input frame,
where each value is the estimated people-per-pixel-region density (sum over
the whole array reproduces `estimated_count`). This is a materially larger
payload than Endpoint A — use Endpoint A for the polling/alerting path that
refreshes every feed every few seconds, and Endpoint B only for the one tile
an operator has open.

---

## 4. Endpoint C — Batch estimate (multiple cameras at once)

**Purpose:** for a dashboard refresh that scores several camera tiles
together rather than issuing one HTTP round-trip per camera.

**Input**
| Field | Type | Required |
|---|---|---|
| `images` | array of binary | yes |
| `camera_ids` | array of string | no, must match `images` length if given |

**Output:** array of Endpoint-A-shaped objects, one per input image, in the
same order.

---

## 5. Error conditions

| Condition | Response |
|---|---|
| Image unreadable / corrupt | HTTP 400, `{"error": "Could not read image: <detail>"}` |
| Image smaller than 64×64px | HTTP 400, `{"error": "Image too small to be a valid crowd-scene frame (...)"}` |
| Model/artifact files missing at startup | Fails fast at startup with `FileNotFoundError`, not at request time |

---

## 6. Example end-to-end request/response (Endpoint A)

**Request**
```
POST /api/crowd/estimate
Content-Type: multipart/form-data
  image: <CAM-04_frame.jpg>
  camera_id: "CAM-04"
```

**Response**
```json
{
  "estimated_count": 342.6,
  "density_level": "critical",
  "camera_id": "CAM-04",
  "density_map_shape": [270, 480]
}
```

---

## 7. Deployment requirements

- **Python:** 3.10+
- **Dependencies:** see `requirements.txt` (torch, torchvision, numpy, Pillow; FastAPI optional depending on backend stack)
- **Compute:** GPU strongly recommended for real-time use across many feeds; CPU inference works but a single 1024px-capped frame takes roughly 150–400ms on CPU vs. well under 50ms on a T4-class GPU — budget accordingly for 14+ concurrent CCTV feeds (report Fig.12.1).
- **Model size:** CSRNet, VGG16-BN frontend + dilated-conv backend, ~16M parameters (~65MB checkpoint file)
- **Storage:** the two artifact files (`crowd_density_model.pt`, `model_config.json`) need to be available to the backend process — via a mounted volume, cloud storage bucket, or bundled into the deployment image.
- **Known limitation carried into deployment:** this model is trained on UCF-QNRF (varied urban crowd scenes, mostly daytime, ground-level and moderately elevated viewpoints), not Wari-corridor CCTV footage specifically. UCF-QNRF's extreme high-density scenes make it a reasonable proxy for Vari-scale crowds, but camera angle, night/low-light footage, and monsoon-season visibility are not represented in training — see the notebook's Limitations section. Flag this to whoever deploys it; expect a fine-tuning pass on real corridor footage before any real-event use, same caveat as the Re-ID component.
