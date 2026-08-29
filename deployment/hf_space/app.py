"""
VariSetu — combined inference Space.

Four tabs, one Space, one free CPU instance:
  1. Crowd Density        (your trained CSRNet)
  2. Fall Detection        (your trained BiLSTM+Attention model)
  3. Person Re-Identification (your trained ResNet50 Re-ID model)
  4. Face Recognition      (pretrained InsightFace buffalo_l — no training needed)

Each tab is exposed as a named API endpoint (api_name=...) so your FastAPI
backend can call it directly with gradio_client, without anyone needing to
click through the UI.

EDIT the three repo IDs below to match what upload_weights.py created.
"""

import json
import os

import cv2
import gradio as gr
import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image

from model_defs import CrowdDensityModelBundle, FallModelBundle, ReIDModelBundle

# ---------------------------------------------------------------------------
# EDIT THESE to match the repo_ids you used in upload_weights.py
# ---------------------------------------------------------------------------
CROWD_REPO = "Saj2005/varisetu-crowd-density"
FALL_REPO = "Saj2005/varisetu-fall-detection"
REID_REPO = "Saj2005/varisetu-person-reid"
# ---------------------------------------------------------------------------

DEVICE = "cpu"  # free Space tier is CPU-only

_crowd_bundle = None
_fall_bundle = None
_reid_bundle = None
_face_engine = None


def get_crowd_bundle():
    global _crowd_bundle
    if _crowd_bundle is None:
        weights = hf_hub_download(CROWD_REPO, "crowd_density_model.pt")
        config = json.load(open(hf_hub_download(CROWD_REPO, "model_config.json")))
        _crowd_bundle = CrowdDensityModelBundle.load(weights, config, device=DEVICE)
    return _crowd_bundle


def get_fall_bundle():
    global _fall_bundle
    if _fall_bundle is None:
        weights = hf_hub_download(FALL_REPO, "fall_model.pt")
        config = json.load(open(hf_hub_download(FALL_REPO, "model_config.json")))
        _fall_bundle = FallModelBundle.load(weights, config, device=DEVICE)
    return _fall_bundle


def get_reid_bundle():
    global _reid_bundle
    if _reid_bundle is None:
        weights = hf_hub_download(REID_REPO, "reid_model.pt")
        config = json.load(open(hf_hub_download(REID_REPO, "model_config.json")))
        _reid_bundle = ReIDModelBundle.load(weights, config, device=DEVICE)
    return _reid_bundle


def get_face_engine():
    """Pretrained InsightFace buffalo_l — downloads its own weights on first call
    (from InsightFace's model zoo, not HF), then stays cached in memory."""
    global _face_engine
    if _face_engine is None:
        from insightface.app import FaceAnalysis
        _face_engine = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _face_engine.prepare(ctx_id=0, det_size=(640, 640))
    return _face_engine


# =============================================================================
# Tab 1 — Crowd Density
# =============================================================================

def crowd_density_predict(image: Image.Image):
    if image is None:
        return {"error": "No image provided"}
    bundle = get_crowd_bundle()
    count = bundle.predict(image.convert("RGB"))
    thresholds = bundle.config.get("density_alert_thresholds", {"moderate_count": 150, "critical_count": 400})
    if count >= thresholds["critical_count"]:
        level = "critical"
    elif count >= thresholds["moderate_count"]:
        level = "moderate"
    else:
        level = "normal"
    return {"estimated_count": round(count, 1), "density_level": level}


# =============================================================================
# Tab 2 — Fall Detection (short video clip)
# =============================================================================

def fall_detection_predict(video_path: str):
    if video_path is None:
        return {"error": "No video provided"}

    bundle = get_fall_bundle()

    # Lightweight, dependency-light substitute for the repo's MediaPipe Tasks
    # PoseLandmarker pipeline: this demo endpoint expects the uploaded clip to
    # already be a single-person crop (as it would arrive from your tracker in
    # production). If you want the exact 103-D pose-landmark feature pipeline
    # from Model2_Fall_Detection/backend/preprocessing.py running here too,
    # copy that file into this Space and swap this block for its
    # PoseFeatureExtractor + SlidingWindowBuffer classes.
    from mediapipe.tasks import python as mp_tasks_python
    from mediapipe.tasks.python import vision as mp_tasks_vision
    import mediapipe as mp
    import math
    from collections import deque

    # Download MediaPipe's own hosted pose-landmarker asset directly
    # (small file, cached in /tmp after the first run on this Space instance).
    import urllib.request
    local_pose_model = "/tmp/pose_landmarker_lite.task"
    if not os.path.isfile(local_pose_model):
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
            "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
            local_pose_model,
        )

    base_options = mp_tasks_python.BaseOptions(model_asset_path=local_pose_model)
    options = mp_tasks_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_tasks_vision.RunningMode.VIDEO,
        num_poses=1,
    )
    landmarker = mp_tasks_vision.PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    ms_per_frame = 1000.0 / fps

    feats, frame_idx = [], 0
    prev_centroid_y, prev_aspect = None, None

    while True:
        ok, frame_bgr = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect_for_video(mp_image, int(frame_idx * ms_per_frame))
        frame_idx += 1

        if not result.pose_landmarks:
            feats.append(np.zeros(bundle.feat_dim, dtype=np.float32))
            continue

        lm = result.pose_landmarks[0]
        xs = np.array([p.x for p in lm], dtype=np.float32)
        ys = np.array([p.y for p in lm], dtype=np.float32)
        vis = np.array([getattr(p, "visibility", 1.0) for p in lm], dtype=np.float32)
        kpt_feats = np.stack([xs, ys, vis], axis=1).reshape(-1)

        centroid_y = float(ys.mean())
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        aspect = float((x1 - x0 + 1e-6) / (y1 - y0 + 1e-6))
        ls, rs, lh, rh = lm[11], lm[12], lm[23], lm[24]
        shoulder_mid = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2])
        hip_mid = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2])
        vec = shoulder_mid - hip_mid
        torso_tilt_deg = math.degrees(math.atan2(abs(vec[0]), abs(vec[1]) + 1e-6))
        dy = 0.0 if prev_centroid_y is None else (centroid_y - prev_centroid_y)
        d_aspect = 0.0 if prev_aspect is None else (aspect - prev_aspect)
        prev_centroid_y, prev_aspect = centroid_y, aspect

        feats.append(np.concatenate([kpt_feats, [dy, torso_tilt_deg, aspect, d_aspect]]).astype(np.float32))

    cap.release()
    landmarker.close()

    if len(feats) < bundle.window_size:
        return {"error": f"Clip too short — need at least {bundle.window_size} frames, got {len(feats)}."}

    feats = np.stack(feats, axis=0)
    W, S = bundle.window_size, bundle.stride
    results = []
    for start in range(0, len(feats) - W + 1, S):
        window = feats[start:start + W]
        results.append(bundle.classify_window(window))

    return {
        "windows_evaluated": len(results),
        "fall_detected": any(r["fall_detected"] for r in results),
        "max_fall_probability": max((r["fall_probability"] for r in results), default=0.0),
        "windows": results,
    }


# =============================================================================
# Tab 3 — Person Re-Identification
# =============================================================================

def reid_compare(image_a: Image.Image, image_b: Image.Image):
    if image_a is None or image_b is None:
        return {"error": "Provide two person-crop images"}
    bundle = get_reid_bundle()
    emb_a = np.array(bundle.embed(image_a.convert("RGB")))
    emb_b = np.array(bundle.embed(image_b.convert("RGB")))
    similarity = float(np.dot(emb_a, emb_b))
    threshold = bundle.verification_threshold
    if threshold is not None and similarity >= threshold:
        label = "high" if (similarity - threshold) >= 0.05 else "medium"
    else:
        label = "low"
    return {"similarity": round(similarity, 4), "confidence_label": label, "threshold_used": threshold}


# =============================================================================
# Tab 4 — Face Recognition (pretrained InsightFace buffalo_l)
# =============================================================================

VERIFICATION_THRESHOLD = 0.1268  # calibrated on LFW, see repo's face_calibration_result.json

def face_compare(image_a: Image.Image, image_b: Image.Image):
    if image_a is None or image_b is None:
        return {"error": "Provide two face images"}
    engine = get_face_engine()

    def get_embedding(pil_img):
        bgr = np.array(pil_img.convert("RGB"))[:, :, ::-1].copy()
        faces = engine.get(bgr)
        if not faces:
            return None
        best = max(faces, key=lambda f: f.det_score)
        return best.normed_embedding

    emb_a, emb_b = get_embedding(image_a), get_embedding(image_b)
    if emb_a is None or emb_b is None:
        return {"error": "No usable face detected in one or both images"}

    similarity = float(np.dot(emb_a, emb_b))
    return {
        "similarity": round(similarity, 4),
        "is_match": similarity >= VERIFICATION_THRESHOLD,
        "threshold_used": VERIFICATION_THRESHOLD,
    }


# =============================================================================
# UI
# =============================================================================

with gr.Blocks(title="VariSetu Models") as demo:
    gr.Markdown("# VariSetu — AI Coordination Layer for Pilgrimage Safety\nFour model endpoints in one Space.")

    with gr.Tab("Crowd Density"):
        img_in = gr.Image(type="pil", label="CCTV frame")
        out1 = gr.JSON()
        btn1 = gr.Button("Estimate")
        btn1.click(crowd_density_predict, inputs=img_in, outputs=out1, api_name="crowd_density")

    with gr.Tab("Fall Detection"):
        vid_in = gr.Video(label="Short clip of one tracked person")
        out2 = gr.JSON()
        btn2 = gr.Button("Analyze")
        btn2.click(fall_detection_predict, inputs=vid_in, outputs=out2, api_name="fall_detection")

    with gr.Tab("Person Re-Identification"):
        with gr.Row():
            reid_a = gr.Image(type="pil", label="Query crop")
            reid_b = gr.Image(type="pil", label="Gallery crop")
        out3 = gr.JSON()
        btn3 = gr.Button("Compare")
        btn3.click(reid_compare, inputs=[reid_a, reid_b], outputs=out3, api_name="person_reid")

    with gr.Tab("Face Recognition"):
        with gr.Row():
            face_a = gr.Image(type="pil", label="Face 1")
            face_b = gr.Image(type="pil", label="Face 2")
        out4 = gr.JSON()
        btn4 = gr.Button("Compare")
        btn4.click(face_compare, inputs=[face_a, face_b], outputs=out4, api_name="face_recognition")

if __name__ == "__main__":
    demo.launch()
