from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneCrowdMetrics, ZoneOut, ZoneUpdate
from app.services.crowd_service import crowd_service

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("", response_model=List[ZoneOut], summary="List all pilgrimage monitoring zones")
async def list_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone).where(Zone.is_active == True).order_by(Zone.name))
    return [ZoneOut.model_validate(z) for z in result.scalars().all()]


@router.get("/{zone_id}", response_model=ZoneOut, summary="Get zone details by ID")
async def get_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    zone = (await db.execute(select(Zone).where(Zone.id == zone_id))).scalar_one_or_none()
    if not zone:
        raise NotFoundException("Zone not found")
    return ZoneOut.model_validate(zone)


@router.post("", response_model=ZoneOut, status_code=status.HTTP_201_CREATED, summary="Create new zone")
async def create_zone(zone_in: ZoneCreate, db: AsyncSession = Depends(get_db)):
    zone = Zone(**zone_in.model_dump())
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return ZoneOut.model_validate(zone)


@router.get("/metrics/crowd", response_model=List[ZoneCrowdMetrics], summary="Get zone-wise density table metrics")
async def get_zone_crowd_metrics(db: AsyncSession = Depends(get_db)):
    """Returns zone-wise density %, trend, and recommended police action for the Crowd Intelligence view."""
    return await crowd_service.get_current_zone_metrics(db)
