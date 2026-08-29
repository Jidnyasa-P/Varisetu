"""
VariSetu - Face recognition (secondary confirmation signal).

This is NOT a trained model -- it wraps the pretrained InsightFace `buffalo_l`
model as-is, per the project decision to keep face recognition as a secondary
confirmation signal alongside the primary Person Re-ID matching, rather than
fine-tune it ourselves (see the dataset-sourcing discussion: no legitimately
licensed pilgrimage-scale face training dataset exists, and re-purposing
retracted datasets like MS-Celeb-1M/MegaFace is a real liability, not just a
technical shortcut).

Used ONLY when a clear, sufficiently large frontal face is detected. If no
usable face is found (dense crowd, side angle, distance, occlusion -- the
norm at a Wari-scale event), this module returns None and the system falls
back to Re-ID appearance matching alone. It never blocks or gates the Re-ID
result -- it only adds a confirming or conflicting signal on top of it.

Requires: insightface, onnxruntime (CPU) or onnxruntime-gpu (GPU).
"""

from dataclasses import dataclass
from typing import Optional, List

import numpy as np
from PIL import Image


@dataclass
class FaceDetection:
    embedding: List[float]     # 512-d, already L2-normalized by InsightFace
    det_score: float           # detector confidence, 0-1
    bbox: List[float]          # [x1, y1, x2, y2] in pixel coordinates


class FaceConfirmationEngine:
    """
    Thin, honest wrapper around InsightFace's pretrained buffalo_l model.

    Calibration note: the `verification_threshold` default below (0.1268) is
    calibrated against LFW verification pairs (Aug 28 2026 run):
      - ROC-AUC: 0.9853
      - At this threshold: Accuracy 0.973, Precision 0.978, Recall 0.968, F1 0.973
      - Achieved FPR 2.2% (targeted ~5%), TPR 96.8%
      - Full result: model/calibration_output/face_calibration_result.json
    This was measured, not guessed -- an earlier placeholder value of 0.42 was
    off by a wide margin from what LFW actually showed once tested.

    IMPORTANT: this is calibrated on LFW (large, frontal, well-lit, well-posed
    faces), NOT on Wari/CCTV-style imagery. Treat it as a validated starting
    point, not a guarantee of the same precision/recall on real crowd-camera
    footage -- flagged the same way as the Re-ID domain-gap limitation.
    """

    def __init__(
        self,
        det_thresh: float = 0.5,
        min_face_size_px: int = 40,
        verification_threshold: float = 0.1268,
        providers: Optional[list] = None,
    ):
        from insightface.app import FaceAnalysis

        self.det_thresh = det_thresh
        self.min_face_size_px = min_face_size_px
        self.verification_threshold = verification_threshold

        self.app = FaceAnalysis(name="buffalo_l", providers=providers or ["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    @staticmethod
    def _pil_to_bgr_ndarray(image: Image.Image) -> np.ndarray:
        rgb = np.array(image.convert("RGB"))
        return rgb[:, :, ::-1].copy()  # RGB -> BGR, what InsightFace/OpenCV expect

    def get_best_face(self, image: Image.Image) -> Optional[FaceDetection]:
        """
        Returns the highest-confidence usable face in the image, or None if
        no face clears the detection-confidence and minimum-size thresholds.
        Returning None is the expected, common case for CCTV crowd crops --
        callers must handle it, not treat it as an error.
        """
        bgr = self._pil_to_bgr_ndarray(image)
        faces = self.app.get(bgr)
        if not faces:
            return None

        best = max(faces, key=lambda f: f.det_score)
        if best.det_score < self.det_thresh:
            return None

        x1, y1, x2, y2 = best.bbox
        if (x2 - x1) < self.min_face_size_px or (y2 - y1) < self.min_face_size_px:
            return None

        return FaceDetection(
            embedding=best.normed_embedding.tolist(),
            det_score=float(best.det_score),
            bbox=[float(v) for v in best.bbox],
        )

    def similarity(self, embedding_a: List[float], embedding_b: List[float]) -> float:
        """Cosine similarity between two normalized face embeddings (dot product == cosine)."""
        return float(np.dot(np.array(embedding_a), np.array(embedding_b)))

    def is_match(self, embedding_a: List[float], embedding_b: List[float]) -> bool:
        return self.similarity(embedding_a, embedding_b) >= self.verification_threshold


# -----------------------------------------------------------------------------
# LFW calibration -- DONE (Aug 28 2026). Result saved at
# model/calibration_output/face_calibration_result.json. To re-calibrate
# (e.g. after a model update, or against a more Wari-realistic image set):
#
#   python calibrate_face_threshold.py --source kaggle --kaggle_path "<path>"
#
# then update `verification_threshold` above with the new chosen_threshold.
# -----------------------------------------------------------------------------
