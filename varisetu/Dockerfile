# VariSetu ML inference service - Cloud Run deployment
# Cloud Run injects $PORT at runtime; the app must listen on it (not a hard-coded port).

FROM python:3.11-slim

WORKDIR /app

# System deps needed by opencv-python-headless / insightface
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn[standard] python-multipart

COPY . .

# reid_model.pt + model_config.json must already be in ./artifacts/ before building
# (see deployment steps -- do not rely on downloading them at container startup).
ENV REID_ARTIFACTS_DIR=artifacts
ENV ENABLE_FACE_CONFIRMATION=true
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
