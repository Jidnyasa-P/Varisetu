# VariSetu — Model 1: Crowd Density Estimation

Trained component 1 of 3 in the VariSetu ML architecture (Crowd Density,
Fall/Medical-Distress, Person Re-ID). This folder is self-contained: the
training notebook, the backend integration code, and the API contract for
whoever wires this into the FastAPI backend alongside the Re-ID component
you already have.

## What's in this folder

```
Varithon_Model1_CrowdDensity.ipynb   <- run this in Google Colab (training)
MODEL_API_CONTRACT_CROWD.md          <- interface spec for the backend team
README.md                            <- this file
backend/
  model_loader.py                    <- loads crowd_density_model.pt once at startup
  preprocessing.py                   <- image -> model input (matches notebook exactly)
  inference.py                       <- the only file the backend needs to import
  requirements.txt                   <- runtime deps for backend/, separate from notebook deps
```

After you run the notebook, it will also produce (in your Google Drive workdir,
not in this folder — copy them in once training is done):
```
model/artifacts/crowd_density_model.pt
model/artifacts/model_config.json
verification_report/verification_report.json
verification_report/per_image_results.csv
verification_report/training_curves.png
verification_report/sample_predictions.png
Model1_CrowdDensity_output.zip        <- all of the above, zipped
```

## Architecture decision (matches your brief's "3 trained + 1 pretrained" rule)

**CSRNet** (Li, Zhang & Chen, CVPR 2018) — VGG16-BN frontend (ImageNet-pretrained,
first 10 conv layers) + a dilated-convolution backend. Fully convolutional
(any input size), output is a single-channel density map; the estimated
head-count is the sum of that map.

Why CSRNet and not MCNN or a from-scratch Bayesian-Loss/DM-Count model:
- MCNN (multi-column CNN) is the older, weaker baseline on very dense scenes
  — worse fit for UCF-QNRF's up-to-12,865-people images and worse fit for
  Vari-scale crowds, which is exactly the failure mode you're building
  against.
- Bayesian Loss / DM-Count (the current state-of-the-art family) need
  materially more training time and tuning than a hackathon Colab session
  affords, and the marginal accuracy gain over CSRNet doesn't change the
  crush-risk *bands* (normal/moderate/critical) that the dashboard actually
  acts on.
- CSRNet is the standard, well-documented middle ground: strong enough to
  be a real, defensible "trained model" (not a toy), light enough to
  actually finish training in Colab, and there's a large body of public
  reference implementations to sanity-check against if something looks off.

## Setup steps

1. **Download the dataset once** from Kaggle: `faihajalamtopu/ucf-qnrf`
   (https://www.kaggle.com/datasets/faihajalamtopu/ucf-qnrf).
2. **Upload it to your Google Drive** — either the extracted folder or the
   zip — e.g. `My Drive/VariSetu/UCF-QNRF/`. The notebook reads from Drive,
   not from a fresh Kaggle download each session, so you don't burn Colab
   time re-downloading on every reconnect.
3. Open `Varithon_Model1_CrowdDensity.ipynb` in Google Colab.
4. **Runtime → Change runtime type → GPU** (a free-tier T4 is enough).
5. In Section 3 of the notebook, edit `DRIVE_DATASET_PATH` to point at
   wherever you put the dataset in step 2.
6. Run all cells top to bottom. Section 10 has a `QUICK_TEST` flag —
   leave it `True` the first run to sanity-check the whole pipeline in
   ~10 minutes, then set it to `False` and re-run that cell for the real
   training run.
7. Checkpoints and cached ground-truth density maps are saved to your Drive
   workdir after every step, so a Colab disconnect does **not** mean
   starting over — just re-run the notebook and it picks up where it left
   off.
8. Section 13 exports `crowd_density_model.pt` + `model_config.json` +
   the verification report, and zips everything into
   `Model1_CrowdDensity_output.zip` on your Drive. Section 14 offers a
   direct browser download of that zip.

Expected time budget on a free-tier T4: ~25–40 min for one-time ground-truth
generation, ~2–3 hrs for a full training run (fewer epochs = a faster but
less accurate model; the notebook's `EPOCHS` constant in Section 10 is the
one knob to shorten this if you're up against a deadline).

## Deploying the trained model to the backend

1. Copy `crowd_density_model.pt` and `model_config.json` from the notebook's
   export into `backend/model/artifacts/` (create that folder).
2. `pip install -r backend/requirements.txt` in the backend's environment.
3. In the FastAPI app, at startup (not per-request):
   ```python
   from model.inference import CrowdDensityInferenceEngine
   density_engine = CrowdDensityInferenceEngine(artifacts_dir="model/artifacts")
   ```
4. See `MODEL_API_CONTRACT_CROWD.md` for the exact request/response shapes
   the dashboard's Crowd Intelligence layer should call.

## Metrics you'll get (not just one accuracy number)

Per the brief's instruction to evaluate "all metrics, not just accuracy",
`verification_report.json` reports:
- **MAE / MSE / RMSE / MAPE** — standard crowd-counting accuracy metrics,
  overall and broken down by density tercile (low/medium/high-count images),
  so a good overall MAE can't hide a model that only works on sparse scenes.
- **GAME(0)–GAME(3)** (Grid Average Mean absolute Error) — splits each image
  into a 1×1, 2×2, 4×4, 8×8 grid and averages the per-cell count error.
  Catches a model that gets the whole-image total right by luck while
  putting the crowd mass in the wrong part of the frame — which matters
  directly for choke-point localization on the dashboard, not just the
  headline number.
- **Density-map PSNR / SSIM** — image-quality metrics comparing the
  predicted density map to the ground-truth map directly, as a second,
  independent check beyond count-derived metrics.
- Sample visualizations (`sample_predictions.png`) — one qualitative
  example per density tercile, so you can eyeball the heatmap quality
  yourself before trusting the numbers.

## Known limitations (carried into `model_config.json`'s `notes` field)

- Trained on UCF-QNRF (varied urban crowd scenes, mostly daytime, ground-
  level to moderately elevated CCTV-style angles) — not on Wari-corridor
  footage. Expect a fine-tuning pass on real corridor CCTV before actual
  event use; UCF-QNRF's extreme density range makes it a reasonable proxy,
  not a perfect match.
- `density_alert_thresholds` (moderate/critical count cutoffs) in
  `model_config.json` are starting defaults for a command-centre dashboard,
  not something the training data can derive — UCF-QNRF has no
  crush-risk labels. Recalibrate these against real Pandharpur corridor
  footage and known choke-point capacities before using them for actual
  alerting.
- Night/low-light and monsoon-season visibility conditions are not
  represented in UCF-QNRF's training images.

## If something looks wrong after training

- **Val MAE not decreasing at all after a few epochs:** check that
  `QUICK_TEST` is `False` and that you're actually on a GPU runtime
  (Section 8 prints a warning if not).
- **Predicted counts wildly off (e.g. all near zero or exploding):**
  almost always a preprocessing mismatch — re-check that `MAX_DIM` in
  Section 5 and `model_config.json`'s `preprocessing.max_dimension` in
  Section 13 agree (they're wired to the same constant automatically in
  this notebook, so this should only come up if you've hand-edited a cell).
- **`FileNotFoundError` in Section 4:** `DRIVE_DATASET_PATH` doesn't point
  at a folder/zip containing `Train/` and `Test/` subfolders — double-check
  the path in your Drive.
