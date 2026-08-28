# VariSetu — Model 2: Fall / Medical-Distress Detection

Part of the 3-trained-model + 1-pretrained-component ML architecture for VariSetu
(Varithon, Team V26-GF-101). This is Model 2 of 3 trained models:

| # | Model | Status |
|---|---|---|
| 1 | Crowd Density Estimation (UCF-QNRF) | not built yet |
| **2** | **Fall / Medical-Distress Detection (MCFD)** | **this package** |
| 3 | Person Re-Identification (Market-1501) | already built (`Varithon_Model_PersonReID.ipynb` + artifacts) |
| — | Marathi ASR (Common Voice Marathi) | pretrained IndicWhisper only, not trained |

## What's in this package

```
train_fall_detection_colab.py        <- run this in Google Colab (Sections 0-9)
backend/
  preprocessing.py                   <- pose feature extraction + sliding window
  model_loader.py                    <- loads fall_model.pt + model_config.json
  inference.py                       <- FallDetectionInferenceEngine (the class the backend calls)
  requirements.txt
MODEL_API_CONTRACT_FALL.md           <- interface spec for whoever wires this into the backend
README.md                            <- this file
```

**What is NOT in this package (and why):** `fall_model.pt`, `model_config.json`,
`metrics.json`, `evaluation_plots.png`, and the zipped model output. Those are
**produced by running the training script** — I don't have your Kaggle dataset
or a GPU here, so I can't train it or hand you real numbers; anything I put in
those files right now would be fabricated. The training script (Section 8)
generates and zips all of them automatically once you run it — see Step-by-step
below. This is the same reason the Re-ID artifacts you already have came out of
running `Varithon_Model_PersonReID.ipynb`, not out of a chat message.

---

## Architecture summary (also documented at the top of the training script)

- **Pretrained, not trained by us:** MediaPipe Pose (BlazePose) — extracts 33
  body keypoints per frame. Same role as ArcFace in the Re-ID model's optional
  face-confirmation path: a pretrained feature extractor we don't fine-tune.
- **Trained by us:** a BiLSTM + attention-pooling temporal classifier over
  45-frame (~1.5s) windows of pose keypoints + 4 engineered kinematic features
  (vertical centroid velocity, torso tilt angle, bbox aspect ratio, aspect-ratio
  delta). Two output heads: binary fall/no-fall (the primary alerting signal)
  and a 3-class no_fall/falling/fallen stage (extra dashboard context).
- **Why this and not a 3D-CNN on raw video:** runs on CPU in real time (matches
  VariSetu's "zero new hardware" USP), is far less prone to overfitting on a
  dataset MCFD's size, and pose is largely lighting/resolution-invariant —
  directly answering the report's own Risk section about CCTV feed quality.

---

## Step-by-step: running the training script in Google Colab

### 1. Get the dataset into Google Drive
1. Download the dataset from Kaggle: `soumicksarker/multiple-cameras-fall-dataset`
   (Kaggle → Download, or `kaggle datasets download -d soumicksarker/multiple-cameras-fall-dataset`
   if you have the Kaggle CLI set up locally).
2. Upload the `.zip` to your Google Drive, e.g. under
   `MyDrive/VariSetu/multiple-cameras-fall-dataset.zip`
   — **you don't need to unzip it yourself**, the script does that into Colab's
   local disk on first run (much faster for frame-by-frame reading than reading
   videos directly off Drive).

### 2. Open Colab and set the runtime
  (pose extraction is CPU-bound via MediaPipe either way, and the BiLSTM is
  small) — a T4 will still speed up the LSTM training loop, so pick GPU if one
  is free, but CPU-only will still finish in reasonable time given MCFD's size.

### 3. Paste in the script
- Open `train_fall_detection_colab.py` and either:
  - **Paste it cell-by-cell**, splitting at each `# %% [Section N]` marker (9
    cells total), **or**
  - Upload the whole `.py` file and run `%run train_fall_detection_colab.py`
    from a single cell (after installing dependencies in Section 0), **or**
  - Use `File > Upload notebook` after converting with Jupytext
    (`jupytext --to notebook train_fall_detection_colab.py`) if you prefer a
    native `.ipynb`.

### 4. Edit the two paths in Section 0
```python
DATA_ROOT = "/content/drive/MyDrive/VariSetu/MCFD"                                # if already unzipped
DRIVE_ZIP_PATH = "/content/drive/MyDrive/VariSetu/multiple-cameras-fall-dataset.zip"  # if zipped
```
Only one needs to actually exist — the script uses `DRIVE_ZIP_PATH` automatically
if `DATA_ROOT` isn't already a valid unzipped folder.

### 5. Run Sections 0–1 first and READ the printout
Section 1 auto-detects how your specific Kaggle download laid out chutes/cameras/
annotation files and prints:
- how many video files and annotation files it found
- a preview of the first annotation file's raw content
- how many videos got at least one fall interval matched

**Stop and read this before continuing.** MCFD annotation layouts vary slightly
across Kaggle re-uploads. If the auto-parser matched 0 videos, or something
looks clearly wrong, there's a manual-override block right under Section 1's
code (`for r in video_records: if r["chute"] == "chute01": r["fall_intervals"] = ...`)
— fix the handful of chutes it got wrong there and re-run just that cell.

### 6. Run Sections 2–8 (no edits needed if Section 1 looked correct)
- Section 2: pose extraction — this is the slowest step (one pass over every
  video). Results are cached to disk (`pose_cache/`), so re-running the whole
  script later won't repeat this unless you delete the cache.
- Section 3–4: builds labeled sliding windows, splits by **chute** (not by
  window) so no scenario leaks across train/val/test.
- Section 5–6: model + training loop, early-stopping on validation macro-F1
  (not accuracy — see below).
- Section 7: full test-set evaluation — accuracy, precision/recall/F1 (macro
  **and** fall-class-specific), ROC-AUC, PR-AUC, confusion matrix, and a
  3-way threshold comparison (0.3 / 0.5 / 0.7) so you can see the
  precision/recall trade-off, not just one number.
- Section 8: exports `fall_model.pt`, `model_config.json`, `metrics.json`,
  `training_history.csv`, `evaluation_plots.png`, zipped into
  `varisetu_fall_model_output.zip` in `/content/`.

### 7. Download the zip
Section 9 has the one-liner (`files.download(...)`) commented out — uncomment
and run it, or just use the Colab file browser sidebar to download
`/content/varisetu_fall_model_output.zip` directly.

### 8. Wire it into the backend
Unzip `fall_model.pt` and `model_config.json` into `backend/model/artifacts/`
(same convention as the Re-ID model's artifacts folder) and follow
`MODEL_API_CONTRACT_FALL.md` for the integration API.

---

## Why macro-F1 for early stopping/model selection, not accuracy

MCFD's fall windows are a minority class once you slide a 45-frame window
across mostly-normal-activity video — a model that just predicts "no_fall"
every time can post a deceptively high accuracy while missing every real fall.
The training loop:
- early-stops on **validation macro-F1**, not accuracy or loss alone,
- trains with a **class-balanced sampler** (falls oversampled during training)
  and a **weighted BCE loss** (`pos_weight` set from the actual class ratio),
- reports **precision, recall, F1 (both macro and fall-class-specific), ROC-AUC,
  PR-AUC, and a full confusion matrix** at three different decision thresholds
  on the held-out test set — not a single accuracy number.

This directly matches your instruction to make sure the model is "effective for
all metrics not just accuracy."

---

---

## Pose extraction: MediaPipe Tasks API (not the legacy `solutions` API)

This script uses `mediapipe.tasks.python.vision.PoseLandmarker` — MediaPipe's
current, actively-supported pose API — instead of the older
`mediapipe.solutions.pose` API. The old API has been dropped from recent
MediaPipe wheels, which is what causes `AttributeError: module 'mediapipe' has
no attribute 'solutions'` if you pin an old MediaPipe version that doesn't have
a matching wheel for Colab's current Python version. The Tasks API needs one
extra one-time step, handled automatically in Section 0: it downloads a small
(~5-10MB) pretrained model bundle, `pose_landmarker_lite.task`, from Google's
model hosting. No manual download needed — just run Section 0 top to bottom.

**If you hit the `AttributeError` above on an older copy of this notebook:**
get the current version of this notebook (this one) — the fix is a rewrite of
the pose-extraction code, not a version pin, so patching the old notebook in
place isn't recommended.

**If you switched Colab runtimes or re-ran an old session:** `Runtime > Restart
session`, then run all cells from the top — a previously-imported `mediapipe`
module can otherwise linger in memory even after `pip install --upgrade`.

---

## Known limitations (also written into `model_config.json` after training)

- MCFD is staged, single-actor, indoor, 8 fixed camera angles — expect a domain
  gap vs. outdoor, multi-person, crowded Wari-corridor footage. Plan a
  fine-tuning/calibration pass on real footage before event use, same caveat
  the Re-ID model carries for Market-1501.
- MediaPipe Pose degrades under heavy occlusion or on very small/distant people
  in dense crowds. In production this model should receive person-crops from
  the upstream detector/tracker (same expectation as the Re-ID model), not raw
  wide-angle CCTV frames.
- The 3-class `falling`/`fallen` stage output is useful dashboard context but
  isn't separately threshold-calibrated to the same rigor as the binary
  fall/no-fall decision — treat the binary output as the alerting signal.

---

## Next
Once you've run this and have `fall_model.pt` + `model_config.json` in hand,
send me the exported `metrics.json` (or just the console output from Section 7)
and I can help interpret it, tune the threshold, or fold it into the combined
demo/report — that only needs one more message and no new code.

After this, we can move to **Model 1 — Crowd Density Estimation (UCF-QNRF)**.
