---
title: VariSetu Models
emoji: 🚩
colorFrom: blue
colorTo: orange
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
---

# VariSetu — Model Inference Space

Four endpoints, one free CPU Space:

- **Crowd Density** — CSRNet, estimates head-count and density level from a CCTV frame
- **Fall Detection** — BiLSTM + attention over MediaPipe pose, classifies a short clip
- **Person Re-Identification** — ResNet50 + BNNeck, cosine similarity between two person crops
- **Face Recognition** — pretrained InsightFace `buffalo_l`, secondary confirmation signal

Each tab is also callable directly via the Gradio API (`api_name` set per
tab) — see the backend integration example for how the VariSetu FastAPI
backend calls these programmatically instead of through the UI.
