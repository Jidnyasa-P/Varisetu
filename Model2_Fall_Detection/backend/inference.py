"""
VariSetu — Model 2 (Fall/Medical-Distress Detection) — inference.py

FallDetectionInferenceEngine: the single entry point the backend calls. Wraps
model_loader.load_fall_model() + preprocessing.py so callers never touch
MediaPipe, torch tensors, or normalization directly.

Usage (load ONCE at startup, e.g. in a FastAPI lifespan handler or module-level
singleton — do not re-instantiate per-request, mirrors the Re-ID contract):

    from model.inference import FallDetectionInferenceEngine
    fall_engine = FallDetectionInferenceEngine(artifacts_dir="model/artifacts")

Per tracked person (one instance of the per-track buffer per active CCTV track
ID — get/create it from your tracker's track-ID -> state map):

    track_state = fall_engine.new_track_state()
    ...
    result = fall_engine.push_frame(track_state, cropped_person_frame_bgr)
    if result is not None:
        # a window completed on this call; result has the classification
        ...
"""

import numpy as np
import torch

from model_loader import load_fall_model
from preprocessing import PoseFeatureExtractor, SlidingWindowBuffer, normalize_window, FEAT_DIM


class TrackState:
    """Per-tracked-person state: pose feature extractor + sliding window buffer.
    Create one per active track ID; discard when the track ends (person leaves
    frame / track lost)."""

    def __init__(self, window_size: int, stride: int):
        self.extractor = PoseFeatureExtractor()
        self.buffer = SlidingWindowBuffer(window_size=window_size, stride=stride)

    def close(self):
        self.extractor.close()


class FallDetectionInferenceEngine:
    def __init__(self, artifacts_dir: str = "model/artifacts", device: str = "cpu"):
        self.bundle = load_fall_model(artifacts_dir, device=device)

    # ---- lifecycle ----------------------------------------------------
    def new_track_state(self) -> TrackState:
        return TrackState(window_size=self.bundle.window_size, stride=self.bundle.stride)

    # ---- per-frame streaming API --------------------------------------
    def push_frame(self, track_state: TrackState, cropped_person_frame_bgr: np.ndarray):
        """Call once per new frame for a tracked person. Returns None most of
        the time (still accumulating); returns a result dict once a window
        completes (every `stride` frames, once at least `window_size` frames
        have been seen for this track)."""
        feat = track_state.extractor.process_frame(cropped_person_frame_bgr)
        track_state.buffer.push(feat)
        if not track_state.buffer.ready():
            return None
        window = track_state.buffer.pop_window()
        return self._classify_window(window)

    # ---- batch / offline API (e.g. re-scoring a stored clip) -----------
    def classify_clip(self, frames_bgr: list):
        """Convenience path for a complete clip (list of cropped-person BGR
        frames) rather than a live stream — extracts pose for all frames, then
        classifies every full window and returns the list of results plus a
        clip-level verdict (max fall probability across windows)."""
        extractor = PoseFeatureExtractor()
        feats = [extractor.process_frame(f) for f in frames_bgr]
        extractor.close()
        feats = np.stack(feats, axis=0) if feats else np.zeros((0, FEAT_DIM), dtype=np.float32)

        results = []
        W, S = self.bundle.window_size, self.bundle.stride
        for start in range(0, max(0, len(feats) - W + 1), S):
            window = feats[start:start + W]
            results.append(self._classify_window(window, offset=start))

        clip_verdict = {
            "fall_detected": any(r["fall_detected"] for r in results),
            "max_fall_probability": max((r["fall_probability"] for r in results), default=0.0),
        }
        return {"windows": results, "clip_verdict": clip_verdict}

    # ---- core ------------------------------------------------------------
    def _classify_window(self, window: np.ndarray, offset: int = None):
        norm = normalize_window(window, self.bundle.feature_mean, self.bundle.feature_std)
        x = torch.from_numpy(norm).float().unsqueeze(0).to(self.bundle.device)  # [1, T, F]

        with torch.no_grad():
            logit_b, logit_m, attn_w = self.bundle.model(x)
            prob_fall = torch.sigmoid(logit_b).item()
            stage_probs = torch.softmax(logit_m, dim=-1).squeeze(0).cpu().numpy().tolist()

        stage_labels = ["no_fall", "falling", "fallen"]
        stage_idx = int(np.argmax(stage_probs))

        return {
            "window_offset_frames": offset,
            "fall_probability": round(float(prob_fall), 4),
            "fall_detected": prob_fall >= self.bundle.threshold,
            "threshold_used": self.bundle.threshold,
            "stage": stage_labels[stage_idx],
            "stage_probabilities": {lbl: round(p, 4) for lbl, p in zip(stage_labels, stage_probs)},
            "confidence_label": _confidence_label(prob_fall, self.bundle.threshold),
        }


def _confidence_label(prob: float, threshold: float) -> str:
    # Same three-tier convention as the Re-ID contract's confidence_label, scaled
    # relative to this model's own recommended threshold rather than a fixed cutoff.
    if prob >= max(threshold + 0.2, 0.85):
        return "high"
    if prob >= threshold:
        return "medium"
    if prob >= threshold - 0.15:
        return "low"
    return "unknown"
