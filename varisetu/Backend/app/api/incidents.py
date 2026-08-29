from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.models.user import User
from app.schemas.incident import (
    IncidentAcknowledgeRequest,
    IncidentCreate,
    IncidentEventOut,
    IncidentOut,
    IncidentResolveRequest,
    IncidentUpdate
)
from app.services.incident_service import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[IncidentOut], summary="List incidents with pagination & filters")
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    type: Optional[IncidentType] = None,
    severity: Optional[IncidentSeverity] = None,
    zone_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    incidents = await incident_service.get_incidents(db, status, type, severity, zone_id, limit, offset)
    return [IncidentOut.model_validate(i) for i in incidents]


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED, summary="Create operational incident")
async def create_incident(
    incident_in: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    incident = await incident_service.create_incident(db, incident_in, user_id=user_id)
    return IncidentOut.model_validate(incident)


@router.get("/{id}", response_model=IncidentOut, summary="Get incident details by ID")
async def get_incident(id: str, db: AsyncSession = Depends(get_db)):
    query = select(Incident).where(Incident.id == id).options(selectinload(Incident.events))
    incident = (await db.execute(query)).scalar_one_or_none()
    if not incident:
        raise NotFoundException("Incident not found")
    return IncidentOut.model_validate(incident)


@router.post("/{id}/acknowledge", response_model=IncidentOut, summary="Acknowledge incident")
async def acknowledge_incident(
    id: str,
    ack_req: Optional[IncidentAcknowledgeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    notes = ack_req.notes if ack_req else None
    incident = await incident_service.acknowledge_incident(db, id, user_id=user_id, notes=notes)
    return IncidentOut.model_validate(incident)


@router.post("/{id}/resolve", response_model=IncidentOut, summary="Resolve incident")
async def resolve_incident(
    id: str,
    resolve_req: IncidentResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    incident = await incident_service.resolve_incident(db, id, resolve_req.resolution_notes, user_id=user_id)
    return IncidentOut.model_validate(incident)


@router.get("/{id}/timeline", response_model=List[IncidentEventOut], summary="Get incident timeline audit events")
async def get_incident_timeline(id: str, db: AsyncSession = Depends(get_db)):
    query = select(IncidentEvent).where(IncidentEvent.incident_id == id).order_by(IncidentEvent.created_at.desc())
    events = (await db.execute(query)).scalars().all()
    return [IncidentEventOut.model_validate(e) for e in events]


@router.get("/events/all", summary="Get real-time chronological audit trail of all operational events")
async def get_all_events(limit: int = 50, db: AsyncSession = Depends(get_db)):
    query = select(IncidentEvent).order_by(IncidentEvent.created_at.desc()).limit(limit)
    events = (await db.execute(query)).scalars().all()
    return [
        {
            "id": e.id,
            "incident_id": e.incident_id,
            "event_type": e.event_type,
            "message": e.message,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in events
    ]

