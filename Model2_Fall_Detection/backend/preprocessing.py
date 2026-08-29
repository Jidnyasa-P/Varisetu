"""
VariSetu — Model 2 (Fall/Medical-Distress Detection) — preprocessing.py

Converts a raw sequence of video frames (as received from the CCTV ingestion
pipeline, already cropped to one tracked person by the upstream detector/tracker,
per Kafka Layer 2/3 in the architecture diagram) into the normalized feature
window the model expects.

This module owns the MediaPipe Pose call (pretrained component — never trained
here) and the exact same 4 engineered features computed during training. If you
change anything here, the model MUST be retrained — the feature layout is fixed
at training time and recorded in model_config.json.

Uses MediaPipe's Tasks API (PoseLandmarker), same as the training notebook —
NOT the legacy `mediapipe.solutions.pose` API, which recent MediaPipe releases
no longer ship. Requires a one-time download of a small pretrained model asset
(pose_landmarker_lite.task); see ensure_pose_model_downloaded() below.
"""

import math
import os
import urllib.request
from collections import deque

import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks_python
from mediapipe.tasks.python import vision as mp_tasks_vision

N_LANDMARKS = 33
LANDMARK_FEATS = N_LANDMARKS * 3  # x, y, visibility
ENGINEERED_FEATS = 4
FEAT_DIM = LANDMARK_FEATS + ENGINEERED_FEATS  # 103

POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
DEFAULT_POSE_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "artifacts", "pose_landmarker_lite.task"
)


def ensure_pose_model_downloaded(model_path: str = DEFAULT_POSE_MODEL_PATH) -> str:
    """Downloads the pretrained pose landmarker model asset if it isn't already
    present locally. Call this once at deployment/startup time — do NOT rely on
    this inside a hot request path in an environment without outbound internet;
    in a locked-down production deployment, download the .task file once during
    the build/setup step and just ship it alongside fall_model.pt instead."""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    if not os.path.isfile(model_path):
        urllib.request.urlretrieve(POSE_MODEL_URL, model_path)
    return model_path


class PoseFeatureExtractor:
    """Stateful, per-track feature extractor. Instantiate ONE per tracked person
    (e.g. keyed by tracker ID) so centroid-velocity / aspect-ratio-delta features
    are computed relative to that person's own previous frame, not a different
    person's. Reset or discard the instance when a track ends.

    Uses PoseLandmarker in VIDEO running mode, which requires monotonically
    increasing timestamps per detect_for_video() call — this class tracks an
    internal frame counter and a caller-supplied fps to generate them, so just
    call process_frame() once per new frame in order; don't call it out of
    order or skip frames without accounting for it (see NOTE in process_frame).
    """

    def __init__(self, model_path: str = DEFAULT_POSE_MODEL_PATH,
                 fps: float = 30.0,
                 min_pose_detection_confidence: float = 0.5,
                 min_pose_presence_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        model_path = ensure_pose_model_downloaded(model_path)
        base_options = mp_tasks_python.BaseOptions(model_asset_path=model_path)
        options = mp_tasks_vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_tasks_vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=min_pose_detection_confidence,
            min_pose_presence_confidence=min_pose_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = mp_tasks_vision.PoseLandmarker.create_from_options(options)
        self._ms_per_frame = 1000.0 / fps
        self._frame_idx = 0
        self._prev_centroid_y = None
        self._prev_aspect = None

    def reset(self):
        """Resets kinematic feature state (velocity/delta) for a fresh track.
        Note: does NOT reset the internal timestamp counter — PoseLandmarker's
        VIDEO mode only requires timestamps to increase, not restart at 0, so
        this is safe to call on a still-live landmarker instance."""
        self._prev_centroid_y = None
        self._prev_aspect = None

    def process_frame(self, frame_bgr: np.ndarray) -> np.ndarray:
        """frame_bgr: a single cropped-person frame (BGR, as from cv2/OpenCV),
        assumed to be the NEXT sequential frame for this track at the fps this
        extractor was constructed with. Returns a [FEAT_DIM] float32 vector.
        All-zero vector if pose detection failed on this frame (caller should
        still append it — the model was trained with these zero-rows present,
        since MCFD footage also has occasional detection dropouts)."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(self._frame_idx * self._ms_per_frame)
        self._frame_idx += 1

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.pose_landmarks:
            return np.zeros(FEAT_DIM, dtype=np.float32)

        lm = result.pose_landmarks[0]  # first (only, since num_poses=1) detected person
        xs = np.array([p.x for p in lm], dtype=np.float32)
        ys = np.array([p.y for p in lm], dtype=np.float32)
        vis = np.array([getattr(p, "visibility", 1.0) for p in lm], dtype=np.float32)
        kpt_feats = np.stack([xs, ys, vis], axis=1).reshape(-1)

        centroid_y = float(ys.mean())
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        aspect = float((x1 - x0 + 1e-6) / (y1 - y0 + 1e-6))

        ls, rs = lm[11], lm[12]
        lh, rh = lm[23], lm[24]
        shoulder_mid = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2])
        hip_mid = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2])
        vec = shoulder_mid - hip_mid
        torso_tilt_deg = math.degrees(math.atan2(abs(vec[0]), abs(vec[1]) + 1e-6))

        dy = 0.0 if self._prev_centroid_y is None else (centroid_y - self._prev_centroid_y)
        d_aspect = 0.0 if self._prev_aspect is None else (aspect - self._prev_aspect)
        self._prev_centroid_y, self._prev_aspect = centroid_y, aspect

        return np.concatenate([kpt_feats, [dy, torso_tilt_deg, aspect, d_aspect]]).astype(np.float32)

    def close(self):
        self._landmarker.close()


class SlidingWindowBuffer:
    """Accumulates per-frame feature vectors for one tracked person and yields a
    model-ready window once `window_size` frames have been collected, sliding
    forward by `stride` each time — mirrors training-time windowing exactly."""

    def __init__(self, window_size: int = 45, stride: int = 15):
        self.window_size = window_size
        self.stride = stride
        self._buf = deque(maxlen=window_size)
        self._since_last_window = 0

    def push(self, feat_vec: np.ndarray):
        self._buf.append(feat_vec)
        self._since_last_window += 1

    def ready(self) -> bool:
        return len(self._buf) == self.window_size and self._since_last_window >= self.stride

    def pop_window(self) -> np.ndarray:
        """Returns [window_size, FEAT_DIM] float32. Call only when ready() is True."""
        self._since_last_window = 0
        return np.stack(list(self._buf), axis=0)


def normalize_window(window: np.ndarray, feature_mean, feature_std) -> np.ndarray:
    """Applies the training-time (mean, std) normalization. `feature_mean` /
    `feature_std` come straight from model_config.json — do not recompute them."""
    mean = np.asarray(feature_mean, dtype=np.float32)
    std = np.asarray(feature_std, dtype=np.float32)
    return (window - mean) / std
