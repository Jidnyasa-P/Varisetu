import os
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.actions import router as actions_router
from app.api.announcements import router as announcements_router
from app.api.auth import router as auth_router
from app.api.cameras import router as cameras_router
from app.api.crowd import router as crowd_router
from app.api.dashboard import router as dashboard_router
from app.api.helpline import router as helpline_router
from app.api.incidents import router as incidents_router
from app.api.lost_persons import router as lost_persons_router
from app.api.medical import router as medical_router
from app.api.notifications import audit_router, demo_router, health_router, notifications_router
from app.api.public import public_router
from app.api.resources import router as resources_router
from app.api.routes import router as routes_router
from app.api.yatra import router as yatra_router
from app.api.zones import router as zones_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.core.redis import redis_client
from app.core.security import decode_token
from app.seed.seed_data import seed_database
from app.services.demo_service import demo_service
from app.websocket.manager import ws_manager

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing VariSetu Command Center Backend...")
    await redis_client.connect()
    await init_db()
    try:
        await seed_database()
    except Exception as e:
        logger.warning(f"Auto-seeding skipped or failed: {e}")

    yield

    # Shutdown sequence
    logger.info("Shutting down VariSetu Command Center Backend...")
    await demo_service.stop()
    await redis_client.disconnect()


app = FastAPI(
    title="VariSetu Command Center API",
    description="Mission-critical command & control backend for Ashadhi Wari pilgrimage crowd safety, biometric lost person reunion, and emergency resource management.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    response.headers["X-App-Name"] = "VariSetu"
    return response


# Ensure uploads directory exists and mount static files
os.makedirs(settings.STORAGE_LOCAL_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.STORAGE_LOCAL_DIR), name="uploads")

# Register REST Routers
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(public_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(actions_router, prefix=settings.API_V1_STR)
app.include_router(yatra_router, prefix=settings.API_V1_STR)
app.include_router(announcements_router, prefix=settings.API_V1_STR)
app.include_router(cameras_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(crowd_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(lost_persons_router, prefix=settings.API_V1_STR)
app.include_router(helpline_router, prefix=settings.API_V1_STR)
app.include_router(medical_router, prefix=settings.API_V1_STR)
app.include_router(resources_router, prefix=settings.API_V1_STR)
app.include_router(routes_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)


# Realtime WebSockets Channels with JWT Verification
@app.websocket("/ws")
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "all", token: Optional[str] = None):
    if settings.AUTH_REQUIRED:
        auth_token = token or websocket.query_params.get("token")
        if not auth_token:
            await websocket.close(code=1008)
            return
        payload = decode_token(auth_token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=1008)
            return

    await ws_manager.connect(websocket, channel=channel)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            logger.debug(f"Received WS message on {channel}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel=channel)
    except Exception as e:
        logger.warning(f"WebSocket error on channel {channel}: {e}")
        ws_manager.disconnect(websocket, channel=channel)


# Direct Frontend UI Mounting on root URL
from pathlib import Path
from fastapi.responses import FileResponse

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "Frontend"

if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")


@app.get("/", summary="Command Center Frontend Dashboard")
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "service": "varisetu-backend", "version": "2.0.0"}


@app.get("/app.js")
async def serve_app_js():
    js_file = FRONTEND_DIR / "app.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return {"detail": "app.js not found"}


@app.get("/styles.css")
async def serve_styles_css():
    css_file = FRONTEND_DIR / "styles.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return {"detail": "styles.css not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

