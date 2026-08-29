from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.crowd import CrowdObservation
from app.schemas.crowd import CrowdForecastResponse, CrowdObservationCreate, CrowdObservationOut
from app.schemas.zone import ZoneCrowdMetrics
from app.services.crowd_service import crowd_service
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/crowd", tags=["Crowd Intelligence"], dependencies=[Depends(get_current_user)])


@router.get("/current", response_model=List[ZoneCrowdMetrics], summary="Get current zone density telemetry")
async def get_current_crowd(db: AsyncSession = Depends(get_db)):
    """Retrieve latest density percentages and police action recommendations across all zones."""
    return await crowd_service.get_current_zone_metrics(db)


@router.get("/history", response_model=List[CrowdObservationOut], summary="Get historical crowd density observations")
async def get_crowd_history(
    zone_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(CrowdObservation).order_by(desc(CrowdObservation.observed_at))
    if zone_id:
        query = query.where(CrowdObservation.zone_id == zone_id)
    query = query.limit(limit)
    result = await db.execute(query)
    return [CrowdObservationOut.model_validate(o) for o in result.scalars().all()]


@router.post("/observations", response_model=CrowdObservationOut, status_code=status.HTTP_201_CREATED, summary="Ingest CCTV crowd telemetry")
async def record_crowd_observation(obs_in: CrowdObservationCreate, db: AsyncSession = Depends(get_db)):
    obs = await crowd_service.record_observation(db, obs_in)
    return CrowdObservationOut.model_validate(obs)


@router.get("/forecast", response_model=CrowdForecastResponse, summary="Get 2-hour congestion forecast model")
async def get_crowd_forecast(db: AsyncSession = Depends(get_db)):
    """Retrieve 2-hour congestion prediction points for Wakhri Phata & Pandharpur Chowk."""
    return await forecast_service.get_2hour_forecast(db)


@router.get("/heatmap", summary="Get normalized crowd heatmap points")
async def get_crowd_heatmap(db: AsyncSession = Depends(get_db)):
    """Retrieve normalized 0.0 - 1.0 weighted GPS points for Google Maps and Leaflet rendering."""
    from app.services.heatmap_service import heatmap_service
    return await heatmap_service.generate_heatmap_points(db)


from fastapi import File, Form, UploadFile
from app.integrations.vision_adapter import vision_adapter


@router.post("/analyze-frame", summary="Analyze CCTV frame for crowd density with HF Space CSRNet model")
async def analyze_crowd_frame(
    file: Optional[UploadFile] = File(None),
    camera_id: str = Form("CAM-04"),
    preset_frame: Optional[str] = Form(None)
):
    """
    Accepts an uploaded image frame or uses preset CCTV frame to estimate
    crowd density using the deployed CSRNet model from Saj2005/VariSetu on HF Space.
    """
    frame_bytes = None
    if file and file.filename:
        frame_bytes = await file.read()
    elif preset_frame:
        import os
        for search_dir in ["Frontend/assets", "Frontend/assets/videos", "Backend/cctv video"]:
            candidate = os.path.join(search_dir, preset_frame)
            if os.path.exists(candidate):
                with open(candidate, "rb") as f:
                    frame_bytes = f.read()
                break

    if not frame_bytes:
        import os
        fallback_file = "Frontend/assets/cctv_highway4_naka.jpg"
        if os.path.exists(fallback_file):
            with open(fallback_file, "rb") as f:
                frame_bytes = f.read()

    res = await vision_adapter.estimate_crowd(camera_id=camera_id, frame=frame_bytes)
    return {
        "success": True,
        "camera_id": camera_id,
        "result": res,
        "timestamp": "2026-08-30T02:00:00Z"
    }


