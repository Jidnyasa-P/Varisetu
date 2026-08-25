import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, StateTransitionException
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class IncidentService:
    @staticmethod
    async def generate_incident_number(db: AsyncSession) -> str:
        count_q = select(func.count(Incident.id))
        res = await db.execute(count_q)
        total = res.scalar() or 0
        return f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{total + 101:04d}"

    @staticmethod
    async def create_incident(
        db: AsyncSession,
        incident_in: IncidentCreate,
        user_id: Optional[str] = None
    ) -> Incident:
        inc_num = await IncidentService.generate_incident_number(db)

        incident = Incident(
            incident_number=inc_num,
            type=incident_in.type,
            severity=incident_in.severity,
            status=IncidentStatus.OPEN,
            source=incident_in.source,
            zone_id=incident_in.zone_id,
            camera_id=incident_in.camera_id,
            latitude=incident_in.latitude,
            longitude=incident_in.longitude,
            title=incident_in.title,
            description=incident_in.description,
            created_by=user_id,
            is_demo=incident_in.is_demo
        )
        db.add(incident)
        await db.flush()

        # Initial event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="INCIDENT_CREATED",
            message=f"Incident {inc_num} reported: {incident.title}",
            actor_user_id=user_id,
            metadata_json={"severity": incident.severity.value, "source": incident.source}
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_CREATED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id,
            new_value={"incident_number": inc_num, "title": incident.title}
        )

        await db.commit()
        await db.refresh(incident)

        # Broadcast realtime WebSocket event
        event_payload = {
            "incident_id": incident.id,
            "incident_number": incident.incident_number,
            "title": incident.title,
            "type": incident.type.value,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "source": incident.source,
            "created_at": incident.created_at.isoformat()
        }
        await ws_manager.broadcast(WebSocketEventType.INCIDENT_CREATED, event_payload, channel="incidents")
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] {incident.incident_number} {incident.title}"},
            channel="dashboard"
        )

        return incident

    @staticmethod
    async def acknowledge_incident(
        db: AsyncSession,
        incident_id: str,
        user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Incident:
        query = select(Incident).where(Incident.id == incident_id).options(selectinload(Incident.events))
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise NotFoundException("Incident not found")

        if incident.status not in (IncidentStatus.OPEN,):
            raise StateTransitionException(incident.status.value, IncidentStatus.ACKNOWLEDGED.value, "Incident")

        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now(timezone.utc)
        incident.assigned_user_id = user_id

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="OFFICER_ACKNOWLEDGED",
            message=f"Incident acknowledged by controller. {notes or ''}".strip(),
            actor_user_id=user_id
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_ACKNOWLEDGED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(incident)

        await ws_manager.broadcast(
            WebSocketEventType.INCIDENT_UPDATED,
            {"incident_id": incident.id, "status": incident.status.value},
            channel="incidents"
        )
        return incident

    @staticmethod
    async def resolve_incident(
        db: AsyncSession,
        incident_id: str,
        resolution_notes: str,
        user_id: Optional[str] = None
    ) -> Incident:
        query = select(Incident).where(Incident.id == incident_id).options(selectinload(Incident.events))
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise NotFoundException("Incident not found")

        if incident.status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
            raise StateTransitionException(incident.status.value, IncidentStatus.RESOLVED.value, "Incident")

        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now(timezone.utc)

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="INCIDENT_RESOLVED",
            message=f"Incident resolved: {resolution_notes}",
            actor_user_id=user_id
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_RESOLVED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(incident)

        await ws_manager.broadcast(
            WebSocketEventType.INCIDENT_UPDATED,
            {"incident_id": incident.id, "status": incident.status.value, "resolved_at": incident.resolved_at.isoformat()},
            channel="incidents"
        )
        return incident

    @staticmethod
    async def get_incidents(
        db: AsyncSession,
        status: Optional[IncidentStatus] = None,
        type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None,
        zone_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Incident]:
        query = select(Incident).options(selectinload(Incident.events)).order_by(Incident.created_at.desc())
        if status:
            query = query.where(Incident.status == status)
        if type:
            query = query.where(Incident.type == type)
        if severity:
            query = query.where(Incident.severity == severity)
        if zone_id:
            query = query.where(Incident.zone_id == zone_id)

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())


incident_service = IncidentService()
