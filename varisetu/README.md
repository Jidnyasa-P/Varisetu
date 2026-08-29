<div align="center">

# 🚩 वारी सेतु &bull; VariSetu
### **Maharashtra State Police IT Cell &bull; Shri Kshetra Pandharpur Smart Pilgrimage Command & Control Platform**

<img src="Frontend/assets/varisetu_logo.png" alt="VariSetu Logo" width="160"/>
<br/>
<img src="Frontend/assets/maharashtra_gov_seal.png" alt="Government of Maharashtra" width="80"/>

[![Backend Status](https://img.shields.io/badge/FastAPI-v2.0.0-009688.svg?style=flat&logo=fastapi)](http://127.0.0.1:8000/docs)
[![Frontend](https://img.shields.io/badge/Frontend-Vite%20%7C%20Vanilla%20JS-646CFF.svg?style=flat&logo=vite)](http://127.0.0.1:5173)
[![Test Suite](https://img.shields.io/badge/Pytest-11%2F11%20Passed%20(100%25)-brightgreen.svg?style=flat&logo=pytest)](Backend/tests/test_api.py)
[![License](https://img.shields.io/badge/Govt.%20Portal-Maharashtra%20Police%20IT%20Cell-maroon.svg)](#)

---

</div>

## 📌 Executive Summary

**VariSetu (वारी सेतु)** is a mission-critical smart command, control, and pilgrim assistance system designed for the **Ashadhi Ekadashi Wari Pilgrimage** in Pandharpur, Maharashtra—one of the world's largest pedestrian gatherings (~8.5 Lakh to 15 Lakh devotees).

The platform bridges real-time field surveillance, AI-based computer vision analytics, multi-agency incident dispatch, and public citizen safety into a unified portal.

---

## 🏛️ System Architecture

```
                                  ┌─────────────────────────────────────────┐
                                  │       VARISETU UNIFIED SYSTEM           │
                                  └────────────────────┬────────────────────┘
                                                       │
                     ┌─────────────────────────────────┴─────────────────────────────────┐
                     │                                                                   │
       ┌─────────────▼─────────────┐                                       ┌─────────────▼─────────────┐
       │   OFFICIAL COMMAND CENTER │                                       │   PUBLIC CITIZEN PORTAL   │
       │     (State Police/Admin)  │                                       │    (Warkaris & Families)  │
       └─────────────┬─────────────┘                                       └─────────────┬─────────────┘
                     │                                                                   │
     ┌───────────────┼───────────────┬───────────────┐                   ┌───────────────┼───────────────┐
     ▼               ▼               ▼               ▼                   ▼               ▼               ▼
┌─────────┐    ┌───────────┐   ┌───────────┐   ┌───────────┐       ┌───────────┐   ┌───────────┐   ┌───────────┐
│ Live 60 │    │ Biometric │   │  Medical  │   │  Traffic  │       │  Palkhi   │   │ Emergency │   │  Citizen  │
│FPS CCTV │    │  Lost &   │   │  Triage   │   │  Dynamic  │       │ Live Route│   │ Helplines │   │  Missing  │
│ Streams │    │   Found   │   │ Dispatch  │   │ Diversion │       │ Tracking  │   │ Directory │   │ Reporting │
└─────────┘    └───────────┘   └───────────┘   └───────────┘       └───────────┘   └───────────┘   └───────────┘
```

---

## 🚀 Key Modules & Capabilities

### 1. 🎥 Real-Time CCTV Surveillance Engine (60 FPS)
- **Organic Motion Video Loop**: High-fidelity 60 FPS video loop rendering continuous devotee flow and camera pans on HTML5 Canvas.
- **Surveillance HUD Overlay**: Live millisecond timestamping (`IST`), blinking recording indicator (`● REC`), camera ID, and stream latency telemetry (12ms).
- **Dynamic AI Detection Bounding Boxes**: Real-time bounding boxes tracking devotees, vehicles, and bottleneck zones with live confidence indicators.
- **Full-Screen Tactical Modal**: Interactive PTZ controls (*Pan Left/Right, Tilt Up/Down, Zoom In/Out, AI Vision Filter, Snapshot*) and instant unit dispatching.

### 2. 👥 Public Citizen & Pilgrim Portal (`/public`)
- **Accessible without login** directly from the portal entry.
- **Live Palkhi Route Map**: Interactive Leaflet map tracking the Sant Tukaram Maharaj Palkhi and Sant Dnyaneshwar Maharaj Palkhi procession towards Pandharpur.
- **One-Touch Emergency Helplines**: Direct calling for Police (`112`), Ambulance (`108`), Lost Person Desk (`1800-233-0099`), and Shri Vitthal Mandir Samiti (`02186-223550`).
- **Weather & Hydration Advisories**: Real-time ambient temperature (34°C), relative humidity (72%), and ORSL rehydration camp status.
- **Citizen Missing Person Reporting**: Enables families to submit missing person details with photographs directly into the police CCTV matching pool.

### 3. 🔍 AI-Assisted Biometric Lost & Found Registry
- **Multi-Photo Upload**: Supports uploading **1 to 5 photos** (frontal face, side profile, full-body attire) with live thumbnail preview chips and delete actions.
- **512-D Face Vector Embedding Slot**: Pre-configured feature extraction pipeline prepared for edge CCTV facial recognition and cross-camera matching.
- **Bilingual Helpline Call Transcripts**: Integrated ASR audio transcripts (Marathi Deccan dialect & English) with automated NER entity extraction.
- **Biometric Dossier Gallery**: Inspectors can review all registered photos, matching frames, similarity confidence scores, and trigger volunteer dispatch or reunion.

### 4. 🚑 Emergency Medical Alerts & Heat-Risk Monitoring
- **Dedicated Dispatch Interface**: `+ Report Medical Emergency` modal on the Medical Alerts dashboard.
- **Triage Categories**: `HEAT_EXHAUSTION`, `DEHYDRATION`, `FALL`, `FAINTING`, `CARDIAC_RISK`, `OTHER`.
- **Computed Heat Index**: Multi-sensor temperature and humidity aggregation with automated health advisories.
- **Mobile Medical Van Dispatch**: Instant unit assignment (e.g. *Van #MV-02 - Dr. Deshmukh*).

### 5. 🤖 Deep Learning AI Vision Models
- **`Model1_CrowdDensity/`**: Deep learning crowd density estimation and congestion heatmap generator.
- **`Model2_Fall_Detection/`**: Pose estimation and motion velocity model for rapid pilgrim fall detection in crowded chokepoints.

### 6. 🔒 Enterprise Security & Government RBAC
- **Strict Role-Based Access Control (RBAC)**:
  - `ADMIN`: Full authority, user provisioning (`+ Add Officer`), audit trail inspection.
  - `COMMANDER`: Command & control, route diversion, broadcast PA announcements.
  - `POLICE`: CCTV monitoring, field volunteer squad dispatch, lost person case management.
  - `MEDICAL`: Ambulance fleet dispatch, heat-risk advisory triage, patient status updates.
- **Authentication**: JWT token authorization, password masking with inline eye toggle, and secure session management.

---

## 📂 Repository Structure

```
VariSetu/
├── Backend/                       # FastAPI High-Performance Backend
│   ├── app/
│   │   ├── api/                   # REST API Endpoints (Auth, CCTV, Incidents, Lost Persons, Medical, Public)
│   │   ├── core/                  # Security (JWT, bcrypt), Database Config, Redis, Logging
│   │   ├── models/                # SQLAlchemy ORM Models (User, Camera, LostPersonCase, MedicalAlert, etc.)
│   │   ├── schemas/               # Pydantic Schemas & Field Validators
│   │   ├── services/              # Business Logic (Lost Person, Incident, Crowd, Demo Services)
│   │   └── websocket/             # Real-time WebSocket Event Dispatchers
│   ├── tests/                     # Pytest Suite (11/11 Passing Tests)
│   ├── requirements.txt           # Python Dependencies
│   └── varisetu.db                # SQLite Operational Database
│
├── Frontend/                      # Government Command Center Web Application
│   ├── assets/                    # Official Government Seal, Marathi Logo, CCTV Procession Feeds
│   ├── index.html                 # Single Page Application (Login, Citizen Portal, Command Dashboard)
│   ├── styles.css                 # Government Portal UI Design System
│   └── app.js                     # 60 FPS CCTV Canvas Player, Navigation, Realtime WebSockets
│
├── Model1_CrowdDensity/           # AI Model 1: Crowd Density Estimation
│   ├── Varithon_Model1_CrowdDensity.ipynb
│   └── backend/                   # Preprocessing & Inference Pipelines
│
├── Model2_Fall_Detection/         # AI Model 2: Real-time Fall & Stampede Detection
│   ├── train_fall_detection_colab.py
│   └── backend/                   # Model Loader & Pose Estimation
│
├── docker-compose.yml             # Container Orchestration
└── COMPLETE_CODE.md               # Monolithic Export of All Codebase Files
```

---

## ⚡ Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the Backend API Server
```bash
cd Backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1 --reload
```
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Base**: `http://127.0.0.1:8000/api`

### 2. Start the Frontend Application
```bash
cd Frontend
npm install
npx vite --port 5173 --host 127.0.0.1
```
- **Web UI**: [http://127.0.0.1:5173](http://127.0.0.1:5173)

### 3. Run Automated Tests
```bash
cd Backend
pytest -v
```

---

## 🔑 Default Official Login Credentials

| Role | Official Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin / Controller** | `control.room@mahapolice.gov.in` | `varisetu2026` | Full Admin + Add Officers |
| **Police Officer** | `police.officer@mahapolice.gov.in` | `varisetu2026` | CCTV, Lost & Found, Patrol |
| **Medical Team** | `medical.team@varisetu.org` | `varisetu2026` | Medical Triage & Ambulances |

*Ordinary pilgrims and citizens can access the **Public Portal** from the login page without credentials.*

---

## 🛡️ License & Authority

Developed for **Maharashtra State Police IT Cell & Government of Maharashtra** for the smart and safe execution of the **Ashadhi Wari Pilgrimage**.
