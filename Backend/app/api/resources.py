from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.resource import Resource, ResourceAvailability, ResourceType
from app.models.user import User
from app.schemas.resource import (
    ResourceCreate,
    ResourceDispatchRequest,
    ResourceOut,
    ResourceStatusUpdateRequest,
    ResourceUpdate
)
from app.services.resource_service import resource_service

router = APIRouter(prefix="/resources", tags=["Resources"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[ResourceOut], summary="List all operational resources & units")
async def list_resources(
    resource_type: Optional[ResourceType] = None,
    availability: Optional[ResourceAvailability] = None,
    db: AsyncSession = Depends(get_db)
):
    resources = await resource_service.get_resources(db, resource_type, availability)
    return [ResourceOut.model_validate(r) for r in resources]


@router.get("/nearby", response_model=List[ResourceOut], summary="Find nearest available resources sorted by distance")
async def get_nearby_resources(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    resource_type: Optional[ResourceType] = None,
    availability: Optional[ResourceAvailability] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Calculates haversine distance to stationed resources and returns sorted nearest units."""
    return await resource_service.get_nearby_resources(db, latitude, longitude, resource_type, availability, limit)


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED, summary="Register new resource asset")
async def create_resource(res_in: ResourceCreate, db: AsyncSession = Depends(get_db)):
    res = Resource(**res_in.model_dump())
    db.add(res)
    await db.commit()
    await db.refresh(res)
    return ResourceOut.model_validate(res)


@router.get("/{id}", response_model=ResourceOut, summary="Get resource details by ID or code")
async def get_resource(id: str, db: AsyncSession = Depends(get_db)):
    query = select(Resource).where((Resource.id == id) | (Resource.resource_code == id)).options(selectinload(Resource.assignments))
    res = (await db.execute(query)).scalar_one_or_none()
    if not res:
        raise NotFoundException("Resource not found")
    return ResourceOut.model_validate(res)


@router.post("/{id}/dispatch", response_model=ResourceOut, summary="Dispatch resource to incident")
async def dispatch_resource(
    id: str,
    dispatch_req: ResourceDispatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    res = await resource_service.dispatch_resource(
        db,
        resource_id=id,
        incident_id=dispatch_req.incident_id,
        notes=dispatch_req.notes,
        user_id=user_id
    )
    return ResourceOut.model_validate(res)


@router.post("/{id}/status", response_model=ResourceOut, summary="Update resource availability & location")
async def update_resource_status(
    id: str,
    status_req: ResourceStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    res = await resource_service.update_status(
        db,
        resource_id=id,
        availability=status_req.availability,
        status_tag=status_req.status_tag,
        latitude=status_req.latitude,
        longitude=status_req.longitude,
        user_id=user_id
    )
    return ResourceOut.model_validate(res)
