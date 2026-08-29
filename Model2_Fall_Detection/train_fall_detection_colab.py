# -*- coding: utf-8 -*-
"""
VariSetu — Model 2: Fall / Medical-Distress Detection
Colab training script (paste into Colab cell-by-cell, split on the `# %%` markers,
or just Runtime > Run all if uploaded as a .py via Jupytext / File > Upload notebook).

ARCHITECTURE DECISION (documented per project ML strategy)
------------------------------------------------------------
This model follows the same "trained model + pretrained component" split used for
Model 3 (Person Re-ID used pretrained-ImageNet ResNet50 backbone + our trained
classifier/embedding head). Here:

  PRETRAINED / NOT TRAINED BY US:
    MediaPipe Pose Landmarker (BlazePose GHUM, via MediaPipe's Tasks API) —
    extracts 33 body keypoints (x, y, z, visibility) per frame. This is a
    feature extractor, exactly analogous to how ArcFace is used
    as a pretrained *optional secondary* signal for Model 3. We do not fine-tune it.

  TRAINED BY US (this script):
    A temporal sequence classifier (BiLSTM + attention pooling) that takes a
    45-frame (~1.5s @ 30fps) sliding-window sequence of pose keypoints + engineered
    kinematic features (centroid vertical velocity/acceleration, torso tilt angle,
    bounding-box aspect ratio and its rate of change) and classifies the window as
    FALL vs NO-FALL (binary head) and additionally NO_FALL / FALLING / FALLEN
    (3-class head) for richer downstream alerting. This matches the report's
    requirement: input is a *temporal pose sequence*, architecture family is
    *pose-estimation + temporal classifier*, distinct from Model 1's static-image
    CNN density regressor.

WHY POSE SEQUENCES INSTEAD OF RAW VIDEO/CNN3D:
  - Runs in real time on CPU/edge boxes at the control centre (no GPU needed for
    inference — matches VariSetu's "zero new hardware" USP).
  - Keypoints are largely invariant to camera resolution/lighting, which matters for
    the report's own risk note about rural/variable CCTV feeds.
  - Much smaller, much less prone to overfitting on a modestly-sized dataset than a
    3D-CNN trained from scratch — this is the same "don't force a heavier model than
    the data justifies" logic used to reject a 4th from-scratch model for ASR.

DATASET: Multiple Cameras Fall Dataset (MCFD), University of Coimbra
  Kaggle: https://www.kaggle.com/datasets/soumicksarker/multiple-cameras-fall-dataset
  24 "chute" scenarios x 8 synchronized camera views, single actor per scenario,
  performing a fall plus confounding ADL events (sitting, crouching, lying down,
  bending) — the confounding events are what make this dataset good for precision/
  recall (not just accuracy): a naive "did the person go low" heuristic will produce
  false positives on sitting/crouching, which this dataset explicitly tests against.

  Distributed as per-chute folders each containing cam1.avi..cam8.avi and an
  annotation file. Because Kaggle mirrors of this dataset have shipped a couple of
  different annotation layouts over time (some ship one CSV per chute with a
  (start_fall, end_fall, start_lying, end_lying, camera_id, ...) tuple; others ship
  a single consolidated annotations file), Section 2 below AUTO-DETECTS the layout
  and prints a diagnostic sample before any labels are trusted. **Read that printout
  before continuing** — if the auto-parser guesses wrong, a manual override block is
  provided right under it.

CREDIT-EFFICIENCY NOTE FOR THE USER:
  Run Sections 0-2 first and READ the printed diagnostics (dataset layout, class
  balance, a couple of sample rows) before running the rest. That's the only part
  that depends on exactly how your Kaggle download unzipped — everything downstream
  (feature extraction, model, training loop, metrics, export) is fixed and doesn't
  need edits.
"""

# %% [Section 0] -------------------------------------------------------------
# ENVIRONMENT SETUP
# ------------------------------------------------------------------------------
# !pip install -q --upgrade mediapipe opencv-python-headless torch torchvision \
#     scikit-learn matplotlib seaborn tqdm pandas
#
# NOTE ON MEDIAPIPE VERSION: this notebook uses MediaPipe's modern **Tasks API**
# (`mediapipe.tasks.python.vision.PoseLandmarker`), not the old
# `mediapipe.solutions.pose` API. The old "solutions" API was removed from recent
# MediaPipe wheels, and pinning an old MediaPipe version is unreliable because
# Colab's Python version doesn't always have a matching wheel for it (that
# mismatch is exactly what causes `AttributeError: module 'mediapipe' has no
# attribute 'solutions'`). The Tasks API works on any current MediaPipe release,
# so just `pip install --upgrade mediapipe` above — no version pin needed.
#
# If you already ran an older version of this notebook in the same Colab
# session, do Runtime > Restart session once after the pip install above, then
# run all cells from the top — a stale import of mediapipe can otherwise linger.

import os
import re
import json
import glob
import math
import zipfile
import random
import datetime
import urllib.request
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
import cv2
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, roc_auc_score,
    average_precision_score, confusion_matrix, classification_report, roc_curve,
    precision_recall_curve,
)
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", DEVICE)

# ------------------------------------------------------------------------------
# DOWNLOAD THE POSE LANDMARKER MODEL ASSET (pretrained — not trained by us)
# ------------------------------------------------------------------------------
# The Tasks API needs a small pretrained model bundle (~5-30MB depending on
# variant) downloaded once. "lite" is the fastest / smallest and is plenty for
# this use case (we only need approximate joint positions, not pixel-perfect
# landmarks). Swap to pose_landmarker_full.task or pose_landmarker_heavy.task
# (same URL pattern) if you want higher accuracy at more compute cost.
POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
POSE_MODEL_PATH = "/content/pose_landmarker_lite.task"

if not os.path.isfile(POSE_MODEL_PATH):
    print(f"Downloading pose landmarker model to {POSE_MODEL_PATH} ...")
    urllib.request.urlretrieve(POSE_MODEL_URL, POSE_MODEL_PATH)
    print("Done.")
else:
    print("Pose landmarker model already present at", POSE_MODEL_PATH)

# ------------------------------------------------------------------------------
# GOOGLE DRIVE MOUNT + DATASET LOCATION
# ------------------------------------------------------------------------------
# You said you'll bring the dataset via a Drive link. Two supported layouts —
# uncomment ONE of the two blocks below.

# --- Option A: dataset already unzipped in your Drive ---
from google.colab import drive
drive.mount('/content/drive')

DATA_ROOT = "/content/drive/MyDrive/VariSetu/MCFD"   # <-- EDIT to your actual path
# Expected: DATA_ROOT/chute01/cam1.avi ... DATA_ROOT/chute24/cam8.avi (+ annotation files)

# --- Option B: dataset is a .zip sitting in Drive, unzip once into Colab's local disk
# (local disk is far faster to read frame-by-frame than Drive over the network) ---
DRIVE_ZIP_PATH = "/content/drive/MyDrive/VariSetu/multiple-cameras-fall-dataset.zip"  # <-- EDIT
LOCAL_EXTRACT_DIR = "/content/mcfd_local"

if not os.path.isdir(DATA_ROOT) and os.path.isfile(DRIVE_ZIP_PATH):
    os.makedirs(LOCAL_EXTRACT_DIR, exist_ok=True)
    print(f"Extracting {DRIVE_ZIP_PATH} -> {LOCAL_EXTRACT_DIR} (one-time, ~a few min) ...")
    with zipfile.ZipFile(DRIVE_ZIP_PATH, 'r') as zf:
        zf.extractall(LOCAL_EXTRACT_DIR)
    DATA_ROOT = LOCAL_EXTRACT_DIR
    print("Done. DATA_ROOT set to:", DATA_ROOT)

ARTIFACT_DIR = "/content/varisetu_fall_artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)


# %% [Section 1] -------------------------------------------------------------
# DISCOVER FILES + ANNOTATION AUTO-DETECTION (READ THE PRINTOUT BEFORE CONTINUING)
# ------------------------------------------------------------------------------

def find_videos(data_root):
    vids = sorted(glob.glob(os.path.join(data_root, "**", "*.avi"), recursive=True))
    if not vids:
        vids = sorted(glob.glob(os.path.join(data_root, "**", "*.mp4"), recursive=True))
    return vids

def find_annotation_files(data_root):
    cands = []
    for ext in ("*.csv", "*.txt"):
        cands += glob.glob(os.path.join(data_root, "**", ext), recursive=True)
    return sorted(cands)

video_paths = find_videos(DATA_ROOT)
annotation_paths = find_annotation_files(DATA_ROOT)

print(f"Found {len(video_paths)} video files under {DATA_ROOT}")
print(f"Found {len(annotation_paths)} candidate annotation files")
print("Sample videos:", video_paths[:3])
print("Sample annotation files:", annotation_paths[:5])

if annotation_paths:
    with open(annotation_paths[0]) as f:
        print("\n--- Preview of", annotation_paths[0], "---")
        for i, line in enumerate(f):
            if i > 8:
                break
            print(line.strip())

# ------------------------------------------------------------------------------
# CHUTE / CAMERA / FALL-WINDOW PARSER
#
# MCFD's canonical annotation format (University of Coimbra release) is one small
# text/CSV file per chute with rows shaped like:
#   camera_id, start_frame_fall, end_frame_fall  (fall = actor is actively falling
#   or lying on the ground after a fall in that frame range; frames outside that
#   range for a "fall chute" are confounding ADL, e.g. walking/sitting/bending)
#
# We parse tolerantly: search each annotation file for rows containing 2-3 integers
# per camera and treat that as a (start,end) fall interval for that camera's video
# in that chute. Chutes with NO fall interval found are treated as pure-negative
# (all frames = no-fall) — MCFD includes some chutes that are ADL-only.
# ------------------------------------------------------------------------------

CHUTE_RE = re.compile(r"(chute\d+)", re.IGNORECASE)
CAM_RE = re.compile(r"cam(\d+)", re.IGNORECASE)
INT_RE = re.compile(r"-?\d+")

def chute_id_from_path(p):
    m = CHUTE_RE.search(p)
    return m.group(1).lower() if m else Path(p).parent.name

def cam_id_from_path(p):
    m = CAM_RE.search(p)
    return int(m.group(1)) if m else None

def parse_annotation_file(path):
    """Returns dict: {camera_id (int or None): [(start_frame, end_frame), ...]}."""
    intervals = defaultdict(list)
    try:
        rows = []
        with open(path) as f:
            for line in f:
                nums = [int(x) for x in INT_RE.findall(line)]
                if len(nums) >= 2:
                    rows.append(nums)
        for nums in rows:
            if len(nums) >= 3:
                cam, a, b = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                cam, a, b = None, nums[0], nums[1]
            else:
                continue
            if a > b:
                a, b = b, a
            if a < 0 or b <= 0:
                continue
            intervals[cam].append((a, b))
    except Exception as e:
        print(f"  [warn] could not parse {path}: {e}")
    return intervals

# Build chute -> annotation-file map (nearest annotation file in same dir tree)
chute_to_annotation = {}
for ap in annotation_paths:
    cid = chute_id_from_path(ap)
    chute_to_annotation.setdefault(cid, []).append(ap)

video_records = []  # list of dicts: path, chute, cam, fall_intervals
for vp in video_paths:
    cid = chute_id_from_path(vp)
    cam = cam_id_from_path(vp)
    fall_intervals = []
    for ap in chute_to_annotation.get(cid, []):
        parsed = parse_annotation_file(ap)
        if cam is not None and cam in parsed:
            fall_intervals.extend(parsed[cam])
        elif None in parsed:  # annotation not camera-specific -> applies to all cams
            fall_intervals.extend(parsed[None])
    video_records.append({"path": vp, "chute": cid, "cam": cam, "fall_intervals": fall_intervals})

n_with_fall = sum(1 for r in video_records if r["fall_intervals"])
print(f"\n{n_with_fall}/{len(video_records)} videos matched at least one fall interval.")
print("If this looks wrong (e.g. 0 matched, or all matched with identical bogus "
      "ranges), inspect the annotation preview above and adjust parse_annotation_file() "
      "— the rest of the pipeline is layout-agnostic once fall_intervals is correct.")

# --- MANUAL OVERRIDE (only if the auto-parser above got it wrong) ---
# Example manual fix if you determine annotations are NOT camera-specific and the
# printed ranges are frame numbers in a single shared column order (start, end):
# for r in video_records:
#     if r["chute"] == "chute01":
#         r["fall_intervals"] = [(500, 620)]


# %% [Section 2] -------------------------------------------------------------
# POSE EXTRACTION (pretrained MediaPipe Tasks API — NOT trained by us)
# ------------------------------------------------------------------------------
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks_python
from mediapipe.tasks.python import vision as mp_tasks_vision

FRAME_STRIDE = 1          # process every frame.
# IMPORTANT: fall_intervals in Section 1 are raw frame numbers straight from the
# annotation files, and Section 3's windowing indexes directly into the pose
# sequence array assuming pose_seq[i] == original video frame i. That equality
# only holds when FRAME_STRIDE == 1. If you raise FRAME_STRIDE to skip frames for
# speed, you MUST also divide every (start, end) in fall_intervals by FRAME_STRIDE
# before Section 3 runs, or every fall window label will be misaligned.
N_LANDMARKS = 33
FEAT_DIM = N_LANDMARKS * 3 + 4   # x,y,visibility per landmark + 4 engineered features

def _make_pose_landmarker(model_path=POSE_MODEL_PATH):
    base_options = mp_tasks_python.BaseOptions(model_asset_path=model_path)
    options = mp_tasks_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_tasks_vision.RunningMode.VIDEO,
        num_poses=1,                          # MCFD is single-actor
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp_tasks_vision.PoseLandmarker.create_from_options(options)


def extract_pose_sequence(video_path, max_frames=None):
    """Returns np.ndarray [T, FEAT_DIM] float32, one row per processed frame.
    Engineered features appended per frame:
      [centroid_dy (vertical centroid velocity, normalized by frame height),
       torso_tilt_deg (angle of shoulder-hip line from vertical),
       bbox_aspect_ratio (w/h of person bbox from landmarks),
       bbox_aspect_ratio_delta (change vs previous frame)]
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0 or math.isnan(fps):
        fps = 30.0   # MCFD source videos are 30fps; safe fallback if metadata is missing
    ms_per_frame = 1000.0 / fps

    frames_feats = []
    prev_centroid_y = None
    prev_aspect = None
    frame_idx = 0
    landmarker = _make_pose_landmarker()
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            if max_frames and frame_idx >= max_frames:
                break
            if frame_idx % FRAME_STRIDE == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                timestamp_ms = int(frame_idx * ms_per_frame)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                if result.pose_landmarks:      # list of detected persons; take first
                    lm = result.pose_landmarks[0]
                    xs = np.array([p.x for p in lm], dtype=np.float32)
                    ys = np.array([p.y for p in lm], dtype=np.float32)
                    vis = np.array([getattr(p, "visibility", 1.0) for p in lm], dtype=np.float32)
                    kpt_feats = np.stack([xs, ys, vis], axis=1).reshape(-1)  # 99

                    centroid_y = float(ys.mean())
                    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
                    aspect = float((x1 - x0 + 1e-6) / (y1 - y0 + 1e-6))

                    ls, rs = lm[11], lm[12]   # shoulders
                    lh, rh = lm[23], lm[24]   # hips
                    shoulder_mid = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2])
                    hip_mid = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2])
                    vec = shoulder_mid - hip_mid
                    torso_tilt_deg = math.degrees(math.atan2(abs(vec[0]), abs(vec[1]) + 1e-6))

                    dy = 0.0 if prev_centroid_y is None else (centroid_y - prev_centroid_y)
                    d_aspect = 0.0 if prev_aspect is None else (aspect - prev_aspect)
                    prev_centroid_y, prev_aspect = centroid_y, aspect

                    row = np.concatenate([kpt_feats, [dy, torso_tilt_deg, aspect, d_aspect]]).astype(np.float32)
                else:
                    row = np.zeros(FEAT_DIM, dtype=np.float32)
                frames_feats.append(row)
            frame_idx += 1
    finally:
        cap.release()
        landmarker.close()
    if not frames_feats:
        return np.zeros((0, FEAT_DIM), dtype=np.float32)
    return np.stack(frames_feats, axis=0)


CACHE_DIR = os.path.join(ARTIFACT_DIR, "pose_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_path_for(video_path):
    key = video_path.replace("/", "_")
    return os.path.join(CACHE_DIR, key + ".npy")

from tqdm import tqdm

for rec in tqdm(video_records, desc="Extracting pose sequences"):
    cp = cache_path_for(rec["path"])
    if os.path.exists(cp):
        continue
    seq = extract_pose_sequence(rec["path"])
    np.save(cp, seq)

print("Pose extraction complete. Cached under", CACHE_DIR)


# %% [Section 3] -------------------------------------------------------------
# WINDOWING: build fixed-length labeled sequences
# ------------------------------------------------------------------------------
WINDOW = 45     # frames (~1.5s @ 30fps)
STRIDE = 15     # 66% overlap between consecutive windows

# 3-class scheme per window based on overlap with fall interval:
#   0 = no_fall (ADL: walking/sitting/crouching/standing/bending/lying-not-from-fall)
#   1 = falling  (window overlaps the transition portion, i.e. first 40% of the interval)
#   2 = fallen   (window overlaps the latter portion, i.e. actor down after the fall)
# Binary label (used as the primary metric target) = 1 if window overlaps the fall
# interval at all, else 0.

def label_window(start, end, fall_intervals):
    binary = 0
    multi = 0  # no_fall
    for (a, b) in fall_intervals:
        overlap = max(0, min(end, b) - max(start, a))
        if overlap > 0:
            binary = 1
            mid = a + 0.4 * (b - a)
            multi = 1 if (start + end) / 2 <= mid else 2
            break
    return binary, multi

samples = []  # (seq[WINDOW, FEAT_DIM], binary_label, multi_label, chute, path)
for rec in video_records:
    cp = cache_path_for(rec["path"])
    if not os.path.exists(cp):
        continue
    seq = np.load(cp)
    T = seq.shape[0]
    if T < WINDOW:
        continue
    for start in range(0, T - WINDOW + 1, STRIDE):
        end = start + WINDOW
        window = seq[start:end]
        # A frame where pose detection failed is stored as an exact all-zero row
        # (see extract_pose_sequence). Count rows that are NOT all-zero, rather
        # than summing the row (engineered features can be negative, so a sum
        # near zero is not a reliable "detection failed" signal).
        valid_frames = np.count_nonzero(np.any(window != 0, axis=1))
        if valid_frames < WINDOW * 0.5:
            continue  # skip windows where pose detection mostly failed
        b, m = label_window(start, end, rec["fall_intervals"])
        samples.append((window, b, m, rec["chute"], rec["path"]))

print(f"Built {len(samples)} labeled windows from {len(video_records)} videos.")
label_counts = Counter(s[1] for s in samples)
print("Binary class balance (0=no_fall, 1=fall):", label_counts)
multi_counts = Counter(s[2] for s in samples)
print("3-class balance (0=no_fall,1=falling,2=fallen):", multi_counts)

if label_counts.get(1, 0) == 0:
    raise RuntimeError(
        "No positive (fall) windows were built. This means Section 1's annotation "
        "parsing did not find valid fall intervals for any video — go back, read the "
        "annotation preview printout, and fix parse_annotation_file() or use the "
        "manual override block before continuing."
    )


# %% [Section 4] -------------------------------------------------------------
# TRAIN / VAL / TEST SPLIT — grouped by CHUTE (not by window!) to prevent leakage.
# Splitting by window would let near-identical overlapping frames from the same
# event appear in both train and test, inflating every metric.
# ------------------------------------------------------------------------------
chutes = np.array([s[3] for s in samples])
X_idx = np.arange(len(samples))

gss1 = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED)
train_idx, temp_idx = next(gss1.split(X_idx, groups=chutes))

gss2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=SEED)
val_idx_rel, test_idx_rel = next(gss2.split(temp_idx, groups=chutes[temp_idx]))
val_idx, test_idx = temp_idx[val_idx_rel], temp_idx[test_idx_rel]

print(f"Split sizes -> train: {len(train_idx)}  val: {len(val_idx)}  test: {len(test_idx)}")
print("Unique chutes per split:",
      len(set(chutes[train_idx])), len(set(chutes[val_idx])), len(set(chutes[test_idx])))

# Normalization stats computed on TRAIN ONLY (avoid leakage)
train_stack = np.concatenate([samples[i][0] for i in train_idx], axis=0)
FEAT_MEAN = train_stack.mean(axis=0)
FEAT_STD = train_stack.std(axis=0) + 1e-6

class FallWindowDataset(Dataset):
    def __init__(self, indices):
        self.indices = indices
    def __len__(self):
        return len(self.indices)
    def __getitem__(self, i):
        window, b, m, chute, path = samples[self.indices[i]]
        window = (window - FEAT_MEAN) / FEAT_STD
        return torch.from_numpy(window).float(), b, m

train_ds = FallWindowDataset(train_idx)
val_ds = FallWindowDataset(val_idx)
test_ds = FallWindowDataset(test_idx)

# Class-balanced sampling for training (falls are the minority class)
train_binary_labels = np.array([samples[i][1] for i in train_idx])
class_sample_count = np.array([np.sum(train_binary_labels == t) for t in [0, 1]])
weight_per_class = 1.0 / np.maximum(class_sample_count, 1)
sample_weights = weight_per_class[train_binary_labels]
sampler = torch.utils.data.WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

BATCH_SIZE = 32
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)


# %% [Section 5] -------------------------------------------------------------
# MODEL: BiLSTM + attention pooling, dual heads (binary fall + 3-class stage)
# ------------------------------------------------------------------------------
class AttentionPool(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.Linear(dim, 1)
    def forward(self, x):  # x: [B, T, dim]
        w = torch.softmax(self.attn(x).squeeze(-1), dim=1)  # [B, T]
        return torch.bmm(w.unsqueeze(1), x).squeeze(1), w   # [B, dim]

class FallDetectionModel(nn.Module):
    def __init__(self, feat_dim=FEAT_DIM, hidden=128, num_layers=2, dropout=0.35):
        super().__init__()
        self.input_norm = nn.LayerNorm(feat_dim)
        self.lstm = nn.LSTM(feat_dim, hidden, num_layers=num_layers, batch_first=True,
                             bidirectional=True, dropout=dropout if num_layers > 1 else 0.0)
        self.pool = AttentionPool(hidden * 2)
        self.drop = nn.Dropout(dropout)
        self.binary_head = nn.Linear(hidden * 2, 1)
        self.stage_head = nn.Linear(hidden * 2, 3)

    def forward(self, x):
        x = self.input_norm(x)
        out, _ = self.lstm(x)
        pooled, attn_w = self.pool(out)
        pooled = self.drop(pooled)
        return self.binary_head(pooled).squeeze(-1), self.stage_head(pooled), attn_w

model = FallDetectionModel().to(DEVICE)
n_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {n_params:,}")


# %% [Section 6] -------------------------------------------------------------
# TRAINING LOOP — early stopping on validation macro-F1 (binary), not accuracy.
# Loss = weighted BCE (binary) + CE (3-class), summed.
# ------------------------------------------------------------------------------
pos_weight = torch.tensor([class_sample_count[0] / max(class_sample_count[1], 1)], device=DEVICE)
bce_loss = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
ce_loss = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=4)

EPOCHS = 60
PATIENCE = 10
best_val_f1 = -1
best_state = None
epochs_no_improve = 0
history = []

def run_epoch(loader, train=True):
    model.train() if train else model.eval()
    total_loss = 0.0
    all_probs, all_bin, all_multi_pred, all_multi_true = [], [], [], []
    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for xb, yb, ym in loader:
            xb, yb, ym = xb.to(DEVICE), yb.float().to(DEVICE), ym.to(DEVICE)
            if train:
                optimizer.zero_grad()
            logit_b, logit_m, _ = model(xb)
            loss = bce_loss(logit_b, yb) + 0.5 * ce_loss(logit_m, ym)
            if train:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                optimizer.step()
            total_loss += loss.item() * xb.size(0)
            all_probs.append(torch.sigmoid(logit_b).detach().cpu().numpy())
            all_bin.append(yb.cpu().numpy())
            all_multi_pred.append(logit_m.argmax(1).detach().cpu().numpy())
            all_multi_true.append(ym.cpu().numpy())
    probs = np.concatenate(all_probs)
    bins = np.concatenate(all_bin)
    preds = (probs >= 0.5).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(bins, preds, average='macro', zero_division=0)
    acc = accuracy_score(bins, preds)
    try:
        auc = roc_auc_score(bins, probs)
    except ValueError:
        auc = float('nan')
    return total_loss / len(loader.dataset), acc, p, r, f1, auc

print("Starting training...")
for epoch in range(1, EPOCHS + 1):
    tr_loss, tr_acc, tr_p, tr_r, tr_f1, tr_auc = run_epoch(train_loader, train=True)
    val_loss, val_acc, val_p, val_r, val_f1, val_auc = run_epoch(val_loader, train=False)
    scheduler.step(val_f1)
    history.append(dict(epoch=epoch, train_loss=tr_loss, val_loss=val_loss,
                         train_f1=tr_f1, val_f1=val_f1, val_auc=val_auc, val_acc=val_acc))
    print(f"Epoch {epoch:02d} | train_loss {tr_loss:.4f} val_loss {val_loss:.4f} "
          f"| val_acc {val_acc:.3f} val_macroF1 {val_f1:.3f} val_AUC {val_auc:.3f}")

    if val_f1 > best_val_f1:
        best_val_f1 = val_f1
        best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        epochs_no_improve = 0
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= PATIENCE:
            print(f"Early stopping at epoch {epoch} (no val macro-F1 improvement for {PATIENCE} epochs).")
            break

model.load_state_dict(best_state)
print(f"Restored best checkpoint (val macro-F1 = {best_val_f1:.4f})")


# %% [Section 7] -------------------------------------------------------------
# FULL EVALUATION ON HELD-OUT TEST SET — every metric that matters, not just accuracy
# ------------------------------------------------------------------------------
model.eval()
all_probs, all_bin, all_multi_logits, all_multi_true = [], [], [], []
with torch.no_grad():
    for xb, yb, ym in test_loader:
        xb = xb.to(DEVICE)
        logit_b, logit_m, _ = model(xb)
        all_probs.append(torch.sigmoid(logit_b).cpu().numpy())
        all_bin.append(yb.numpy())
        all_multi_logits.append(logit_m.cpu().numpy())
        all_multi_true.append(ym.numpy())

test_probs = np.concatenate(all_probs)
test_bin = np.concatenate(all_bin)
test_multi_logits = np.concatenate(all_multi_logits)
test_multi_true = np.concatenate(all_multi_true)
test_multi_pred = test_multi_logits.argmax(1)

# --- Threshold selection: pick the operating point that maximizes recall at a
# minimum-acceptable precision (missed falls are worse than a false alarm the
# control-room officer has to dismiss — but too many false alarms erode trust,
# so we don't just optimize recall alone). Report metrics at 3 operating points.
def metrics_at_threshold(probs, y_true, thr):
    preds = (probs >= thr).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(y_true, preds, average='macro', zero_division=0)
    p_pos, r_pos, f1_pos, _ = precision_recall_fscore_support(y_true, preds, average='binary', zero_division=0)
    acc = accuracy_score(y_true, preds)
    tn, fp, fn, tp = confusion_matrix(y_true, preds, labels=[0, 1]).ravel()
    return dict(threshold=thr, accuracy=acc, macro_precision=p, macro_recall=r, macro_f1=f1,
                fall_precision=p_pos, fall_recall=r_pos, fall_f1=f1_pos,
                true_positive=int(tp), false_positive=int(fp), false_negative=int(fn), true_negative=int(tn))

candidate_thresholds = [0.3, 0.5, 0.7]
threshold_report = [metrics_at_threshold(test_probs, test_bin, t) for t in candidate_thresholds]

# Pick recommended threshold = highest recall among thresholds with fall_precision >= 0.6,
# falling back to 0.5 if none qualify.
qualifying = [m for m in threshold_report if m["fall_precision"] >= 0.6]
recommended = max(qualifying, key=lambda m: m["fall_recall"]) if qualifying else \
              next(m for m in threshold_report if m["threshold"] == 0.5)

roc_auc = roc_auc_score(test_bin, test_probs)
pr_auc = average_precision_score(test_bin, test_probs)

print("\n=== TEST SET REPORT (binary fall / no-fall) ===")
for m in threshold_report:
    print(m)
print("Recommended operating threshold:", recommended["threshold"])
print(f"ROC-AUC: {roc_auc:.4f}   PR-AUC (average precision): {pr_auc:.4f}")

print("\n=== TEST SET — sklearn classification_report at recommended threshold ===")
recommended_preds = (test_probs >= recommended["threshold"]).astype(int)
print(classification_report(test_bin, recommended_preds, target_names=["no_fall", "fall"], zero_division=0))

print("\n=== 3-CLASS STAGE REPORT (no_fall / falling / fallen) ===")
print(classification_report(test_multi_true, test_multi_pred,
                             target_names=["no_fall", "falling", "fallen"], zero_division=0))

# --- Plots ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

cm = confusion_matrix(test_bin, recommended_preds, labels=[0, 1])
im = axes[0].imshow(cm, cmap="Blues")
axes[0].set_title(f"Confusion Matrix (binary, thr={recommended['threshold']})")
axes[0].set_xticks([0, 1]); axes[0].set_xticklabels(["no_fall", "fall"])
axes[0].set_yticks([0, 1]); axes[0].set_yticklabels(["no_fall", "fall"])
axes[0].set_xlabel("Predicted"); axes[0].set_ylabel("True")
for i in range(2):
    for j in range(2):
        axes[0].text(j, i, str(cm[i, j]), ha="center", va="center",
                      color="white" if cm[i, j] > cm.max() / 2 else "black")

fpr, tpr, _ = roc_curve(test_bin, test_probs)
axes[1].plot(fpr, tpr, label=f"ROC (AUC={roc_auc:.3f})")
axes[1].plot([0, 1], [0, 1], linestyle="--", color="gray")
axes[1].set_xlabel("False Positive Rate"); axes[1].set_ylabel("True Positive Rate")
axes[1].set_title("ROC Curve"); axes[1].legend()

prec, rec, _ = precision_recall_curve(test_bin, test_probs)
axes[2].plot(rec, prec, label=f"PR (AP={pr_auc:.3f})")
axes[2].set_xlabel("Recall"); axes[2].set_ylabel("Precision")
axes[2].set_title("Precision-Recall Curve"); axes[2].legend()

plt.tight_layout()
plot_path = os.path.join(ARTIFACT_DIR, "evaluation_plots.png")
plt.savefig(plot_path, dpi=150)
plt.show()
print("Saved evaluation plots to", plot_path)


# %% [Section 8] -------------------------------------------------------------
# EXPORT ARTIFACTS — model weights, config, metrics, plots -> zip
# (Mirrors the Model 3 / Person Re-ID export convention: <model>.pt + model_config.json)
# ------------------------------------------------------------------------------
MODEL_PATH = os.path.join(ARTIFACT_DIR, "fall_model.pt")
torch.save({"model_state_dict": model.state_dict(),
            "architecture": "FallDetectionModel_BiLSTM_AttnPool"}, MODEL_PATH)

config = {
    "model_name": "varisetu_fall_detection",
    "architecture": "pose_sequence_bilstm_attention",
    "pose_backend": "mediapipe_tasks_pose_landmarker_lite (BlazePose GHUM, pretrained, not fine-tuned)",
    "pose_model_asset_url": POSE_MODEL_URL,
    "input_window_frames": WINDOW,
    "input_stride_frames": STRIDE,
    "feature_dim_per_frame": FEAT_DIM,
    "feature_layout": (
        "[0:99] = 33 MediaPipe landmarks x (x,y,visibility); "
        "[99] centroid vertical velocity (normalized frame units/frame); "
        "[100] torso tilt angle from vertical (degrees); "
        "[101] person bbox aspect ratio (w/h); "
        "[102] frame-to-frame delta of bbox aspect ratio"
    ),
    "feature_mean": FEAT_MEAN.tolist(),
    "feature_std": FEAT_STD.tolist(),
    "assumed_source_fps": 30,
    "hidden_size": 128,
    "num_lstm_layers": 2,
    "bidirectional": True,
    "outputs": {
        "binary_head": "fall probability, sigmoid, 1 logit",
        "stage_head": "3-class softmax: [no_fall, falling, fallen]"
    },
    "recommended_binary_threshold": recommended["threshold"],
    "threshold_selection_policy": "highest recall among thresholds with fall_precision >= 0.60",
    "dataset": "Multiple Cameras Fall Dataset (MCFD), University of Coimbra (Kaggle mirror: soumicksarker/multiple-cameras-fall-dataset)",
    "split_strategy": "GroupShuffleSplit by chute (scenario) id — 70/15/15 train/val/test, no chute appears in more than one split",
    "trained_epochs_run": len(history),
    "best_val_macro_f1": best_val_f1,
    "exported_at_utc": datetime.datetime.utcnow().isoformat(),
    "final_test_metrics": {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "at_recommended_threshold": recommended,
        "all_thresholds_evaluated": threshold_report,
    },
    "known_limitations": [
        "Trained on staged single-actor indoor falls (MCFD); expect a domain gap vs "
        "outdoor, multi-person, crowded Wari-corridor CCTV footage — same caveat the "
        "Person Re-ID model carries for Market-1501 vs real deployment footage.",
        "MediaPipe Pose degrades on heavy occlusion / very small or very distant "
        "persons in dense crowds; in production this feeds from a person-detector "
        "crop (as Model 3's Re-ID does), not raw wide-angle frames.",
        "Binary 'fall' vs 'no_fall' the recommended trigger for alerting; the 3-class "
        "'falling'/'fallen' stage output is informative context for the dashboard, "
        "not yet separately threshold-tuned to the same rigor.",
    ],
}
CONFIG_PATH = os.path.join(ARTIFACT_DIR, "model_config.json")
with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)

METRICS_PATH = os.path.join(ARTIFACT_DIR, "metrics.json")
with open(METRICS_PATH, "w") as f:
    json.dump({
        "history": history,
        "test_threshold_report": threshold_report,
        "recommended": recommended,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "stage_classification_report": classification_report(
            test_multi_true, test_multi_pred,
            target_names=["no_fall", "falling", "fallen"], zero_division=0, output_dict=True),
    }, f, indent=2)

HISTORY_CSV = os.path.join(ARTIFACT_DIR, "training_history.csv")
pd.DataFrame(history).to_csv(HISTORY_CSV, index=False)

ZIP_PATH = "/content/varisetu_fall_model_output.zip"
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in [MODEL_PATH, CONFIG_PATH, METRICS_PATH, HISTORY_CSV, plot_path]:
        zf.write(p, arcname=os.path.basename(p))

print("\n=== EXPORT COMPLETE ===")
print("Model:", MODEL_PATH)
print("Config:", CONFIG_PATH)
print("Metrics:", METRICS_PATH)
print("Zip (download this):", ZIP_PATH)
print("\nNext: download", ZIP_PATH, "and unzip fall_model.pt + model_config.json into")
print("backend/model/artifacts/ alongside the reid artifacts (see MODEL_API_CONTRACT_FALL.md).")

# %% [Section 9 - optional] ---------------------------------------------------
# from google.colab import files
# files.download(ZIP_PATH)
