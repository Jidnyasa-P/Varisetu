from typing import List, Optional
from datetime import datetime, timezone, timedelta
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
    ResourceAllocationHistoryItem,
    ResourceCategoryInventory,
    ResourceCreate,
    ResourceDispatchRequest,
    ResourceInventorySummary,
    ResourceOut,
    ResourceStatusUpdateRequest,
    ResourceUpdate
)
from app.services.resource_service import resource_service

router = APIRouter(prefix="/resources", tags=["Resources"], dependencies=[Depends(get_current_user)])


@router.get("/summary", response_model=ResourceInventorySummary, summary="Get 4 resource categories inventory summary (limit: 20 per type)")
async def get_resource_inventory_summary(db: AsyncSession = Depends(get_db)):
    """Returns fixed 20-unit quota per category with dispatched vs available breakdown across the 4 key operational resources."""
    return ResourceInventorySummary(
        total_fleet_limit=80,
        total_dispatched=38,
        total_available=42,
        categories=[
            ResourceCategoryInventory(
                resource_type=ResourceType.WATER_TANKER,
                display_name="Water Tankers (10,000L)",
                total_quota_limit=20,
                dispatched_count=6,
                available_count=14,
                dispatched_units=["WT-01", "WT-04", "WT-07", "WT-09", "WT-12", "WT-15"],
                available_units=["WT-02", "WT-03", "WT-05", "WT-06", "WT-08", "WT-10", "WT-11", "WT-13", "WT-14", "WT-16", "WT-17", "WT-18", "WT-19", "WT-20"],
                key_deployment_locations=["Sector 3 (Narayangaon Km 84)", "Sector 3 (Sangamner)", "Sector 2 (Manchar)", "Sector 1 (Alandi)", "Sector 4 (Nashik)"],
                status_tag="OPTIMAL"
            ),
            ResourceCategoryInventory(
                resource_type=ResourceType.MEDICAL_VAN,
                display_name="Mobile Medical Vans & Ambulances",
                total_quota_limit=20,
                dispatched_count=8,
                available_count=12,
                dispatched_units=["MV-01", "MV-02", "MV-03", "MV-05", "MV-08", "MV-11", "MV-14", "MV-17"],
                available_units=["MV-04", "MV-06", "MV-07", "MV-09", "MV-10", "MV-12", "MV-13", "MV-15", "MV-16", "MV-18", "MV-19", "MV-20"],
                key_deployment_locations=["Sector 3 (Narayangaon Emergency Camp)", "Sector 1 (Bhosari Base)", "Sector 3 (Sangamner ICU Point)", "Sector 4 (Nashik Terminal)"],
                status_tag="ACTIVE"
            ),
            ResourceCategoryInventory(
                resource_type=ResourceType.POLICE_SQUAD,
                display_name="Police Patrol Squads",
                total_quota_limit=20,
                dispatched_count=11,
                available_count=9,
                dispatched_units=["PS-01", "PS-03", "PS-06", "PS-08", "PS-09", "PS-11", "PS-14", "PS-15", "PS-16", "PS-18", "PS-20"],
                available_units=["PS-02", "PS-04", "PS-05", "PS-07", "PS-10", "PS-12", "PS-13", "PS-17", "PS-19"],
                key_deployment_locations=["Sector 4 (Nashik Terminal Security)", "Sector 3 (Narayangaon Chokepoint)", "Sector 2 (Manchar Chowk)", "Sector 1 (Kothrud Origin)"],
                status_tag="SURGE_DEPLOYED"
            ),
            ResourceCategoryInventory(
                resource_type=ResourceType.VOLUNTEER_TEAM,
                display_name="Volunteer Dindi Stewards",
                total_quota_limit=20,
                dispatched_count=13,
                available_count=7,
                dispatched_units=["VT-01", "VT-03", "VT-04", "VT-07", "VT-08", "VT-09", "VT-11", "VT-12", "VT-14", "VT-15", "VT-17", "VT-18", "VT-20"],
                available_units=["VT-02", "VT-05", "VT-06", "VT-10", "VT-13", "VT-16", "VT-19"],
                key_deployment_locations=["Sector 2 (Manchar Bypass Queue)", "Sector 3 (Pilgrim Hydration Lane)", "Sector 1 (Departure Ghats)", "Sector 4 (Govind Nagar Plaza)"],
                status_tag="ACTIVE"
            )
        ]
    )



@router.get("/allocations/history", response_model=List[ResourceAllocationHistoryItem], summary="Get chronological resource allocation and dispatch history")
@router.get("/history", response_model=List[ResourceAllocationHistoryItem], summary="Get resource allocation history")
async def get_resource_allocation_history(db: AsyncSession = Depends(get_db)):
    """Returns chronological allocation and dispatch history for all fleet and emergency resources across corridor sectors."""
    now = datetime.now(timezone.utc)
    return [
        ResourceAllocationHistoryItem(
            id="alloc-hist-01",
            resource_code="WT-09",
            resource_name="10,000L Water Tanker #09",
            resource_type=ResourceType.WATER_TANKER,
            allocated_capacity="10,000 Litres Hydration",
            target_sector="Sector 3 (Manchar ➔ Sangamner)",
            target_location="Narayangaon Transit Camp (Km 84 on NH-60)",
            assigned_at=now - timedelta(minutes=45),
            status="ON_SCENE",
            authorized_by="Command Center Controller",
            purpose="Surge crowd hydration & mist sprayer supply at bottleneck",
            duration="Active (45 mins)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-02",
            resource_code="MV-02",
            resource_name="Mobile Medical Van #02 (Ambulance)",
            resource_type=ResourceType.MEDICAL_VAN,
            allocated_capacity="4 Beds / ICU Telemetry Unit",
            target_sector="Sector 3 (Manchar ➔ Sangamner)",
            target_location="Narayangaon Km 84 Emergency Post",
            assigned_at=now - timedelta(hours=1, minutes=20),
            status="ACTIVE",
            authorized_by="Dr. Shubhada Deshmukh",
            purpose="Emergency medical standby & first aid triage",
            duration="Active (1h 20m)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-03",
            resource_code="PS-14",
            resource_name="Police Patrol Squad #14",
            resource_type=ResourceType.POLICE_SQUAD,
            allocated_capacity="8 Officers (QRT Unit)",
            target_sector="Sector 4 (Sangamner ➔ Nashik)",
            target_location="Govind Nagar Terminal, Nashik",
            assigned_at=now - timedelta(hours=2),
            status="ON_SCENE",
            authorized_by="Inspector Vikram Jadhav",
            purpose="Biometric CCTV match verification & crowd corridor security",
            duration="Active (2h 00m)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-04",
            resource_code="WT-04",
            resource_name="10,000L Water Tanker #04",
            resource_type=ResourceType.WATER_TANKER,
            allocated_capacity="10,000 Litres Hydration",
            target_sector="Sector 3 (Manchar ➔ Sangamner)",
            target_location="Sangamner North Chowk Station",
            assigned_at=now - timedelta(hours=3, minutes=10),
            status="DEPLOYED",
            authorized_by="Inspector R. K. Patil",
            purpose="Replenishing Water Station Hub #4 & ORSL packet distribution",
            duration="Active (3h 10m)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-05",
            resource_code="MV-03",
            resource_name="Emergency Mobile ICU #03",
            resource_type=ResourceType.MEDICAL_VAN,
            allocated_capacity="2 Trauma ICU Beds",
            target_sector="Sector 3 (Manchar ➔ Sangamner)",
            target_location="Sangamner Base Hospital Point",
            assigned_at=now - timedelta(hours=4),
            status="ACTIVE",
            authorized_by="Dr. Shubhada Deshmukh",
            purpose="Cardiac risk monitoring and heat stroke resuscitation standby",
            duration="Active (4h 00m)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-06",
            resource_code="VT-08",
            resource_name="Dindi Volunteer Stewards (Squad 8)",
            resource_type=ResourceType.VOLUNTEER_TEAM,
            allocated_capacity="25 Stewards",
            target_sector="Sector 2 (Bhosari ➔ Manchar)",
            target_location="Manchar Junction Pedestrian Bypass",
            assigned_at=now - timedelta(hours=5, minutes=30),
            status="ACTIVE",
            authorized_by="Command Center Controller",
            purpose="Pilgrim foot traffic separation & bypass diversion assistance",
            duration="Active (5h 30m)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-07",
            resource_code="MV-01",
            resource_name="Mobile Medical Ambulance #01",
            resource_type=ResourceType.MEDICAL_VAN,
            allocated_capacity="4 Beds / Standard Triage",
            target_sector="Sector 1 (Pune ➔ Bhosari)",
            target_location="Bhosari Sector 1 Base Post",
            assigned_at=now - timedelta(hours=6),
            status="STANDBY",
            authorized_by="Command Center Controller",
            purpose="Corridor entry reserve and emergency backup staging",
            duration="Active Standby (6h)"
        ),
        ResourceAllocationHistoryItem(
            id="alloc-hist-08",
            resource_code="WT-12",
            resource_name="10,000L Water Tanker #12",
            resource_type=ResourceType.WATER_TANKER,
            allocated_capacity="10,000 Litres Hydration",
            target_sector="Sector 1 (Pune ➔ Bhosari)",
            target_location="Kothrud Depo Origin Point",
            assigned_at=now - timedelta(hours=8),
            status="COMPLETED",
            authorized_by="Command Center Controller",
            purpose="Morning departure hydration quota distribution",
            duration="Completed (Shift Logged)"
        )
    ]


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


@router.post("/{id}/reassign", response_model=ResourceOut, summary="Reassign resource sector & broadcast update")
async def reassign_resource(
    id: str,
    status_req: ResourceStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    res = await resource_service.update_status(
        db,
        resource_id=id,
        availability=status_req.availability or ResourceAvailability.ASSIGNED,
        status_tag=status_req.status_tag or "REASSIGNED",
        latitude=status_req.latitude,
        longitude=status_req.longitude,
        user_id=user_id
    )
    return ResourceOut.model_validate(res)

