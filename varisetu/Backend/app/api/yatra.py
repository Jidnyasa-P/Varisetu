from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import get_current_user
from app.schemas.yatra import PublicYatraOut, YatraCheckpointOut, YatraLiveOut, YatraTrackPointInput
from app.services.yatra_service import yatra_service

router = APIRouter(prefix="/yatra", tags=["Yatra / Palkhi Tracking"])


@router.get("/live", response_model=YatraLiveOut, summary="Get live Yatra / Palkhi telemetry")
async def get_yatra_live(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Returns high-precision live GPS coordinates, speed, heading, checkpoints, and data freshness age."""
    return await yatra_service.get_live_status(db)


@router.post("/track", response_model=YatraLiveOut, summary="Ingest GPS telemetry point")
async def ingest_yatra_point(
    point: YatraTrackPointInput,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ingests raw or device GPS telemetry, validates sanity bounds, and triggers real-time updates."""
    try:
        return await yatra_service.record_telemetry(db, point)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/checkpoints", response_model=List[YatraCheckpointOut], summary="Get pilgrimage route checkpoints")
async def get_checkpoints():
    """Returns the ordered list of sacred pilgrimage halt checkpoints with ETA progression."""
    return yatra_service.get_checkpoints()
