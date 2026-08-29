from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.exceptions import NotFoundException, StateTransitionException
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.medical import MedicalAlert, MedicalAlertStatus, MedicalAlertType
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability
from app.schemas.medical import MedicalAlertCreate
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class MedicalService:
    @staticmethod
    async def generate_alert_code(db: AsyncSession) -> str:
        count_q = select(func.count(MedicalAlert.id))
        res = await db.execute(count_q)
        total = res.scalar() or 0
        return f"MED-{total + 101:03d}"

    @staticmethod
    async def create_alert(
        db: AsyncSession,
        alert_in: MedicalAlertCreate,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert_code = await MedicalService.generate_alert_code(db)

        # Automatically create linked operational incident
        incident = Incident(
            incident_number=f"INC-{alert_code}",
            type=IncidentType.MEDICAL,
            severity=alert_in.severity,
            status=IncidentStatus.OPEN,
            source="MEDICAL_SENSOR",
            zone_id=alert_in.zone_id,
            camera_id=alert_in.camera_id,
            latitude=alert_in.latitude,
            longitude=alert_in.longitude,
            title=f"Medical Emergency: {alert_in.type.value.replace('_', ' ')}",
            description=alert_in.description,
            created_by=user_id,
            is_demo=alert_in.is_demo
        )
        db.add(incident)
        await db.flush()

        alert = MedicalAlert(
            alert_code=alert_code,
            incident_id=incident.id,
            type=alert_in.type,
            severity=alert_in.severity,
            zone_id=alert_in.zone_id,
            camera_id=alert_in.camera_id,
            latitude=alert_in.latitude,
            longitude=alert_in.longitude,
            description=alert_in.description,
            status=MedicalAlertStatus.ACTIVE,
            assigned_volunteer_name=alert_in.assigned_volunteer_name,
            is_demo=alert_in.is_demo
        )
        db.add(alert)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_CREATED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id,
            new_value={"alert_code": alert_code, "type": alert.type.value}
        )

        await db.commit()
        await db.refresh(alert)

        # Broadcast realtime alerts
        event_payload = {
            "alert_id": alert.id,
            "alert_code": alert.alert_code,
            "type": alert.type.value,
            "severity": alert.severity.value,
            "description": alert.description,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat()
        }
        await ws_manager.broadcast(WebSocketEventType.MEDICAL_ALERT_CREATED, event_payload, channel="medical")
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] {alert.alert_code} {alert.description}"},
            channel="dashboard"
        )
        return alert

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: str,
        volunteer_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        query = select(MedicalAlert).where(MedicalAlert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            raise NotFoundException("Medical alert not found")

        if alert.status not in (MedicalAlertStatus.ACTIVE,):
            raise StateTransitionException(alert.status.value, MedicalAlertStatus.ACKNOWLEDGED.value, "MedicalAlert")

        alert.status = MedicalAlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        if volunteer_name:
            alert.assigned_volunteer_name = volunteer_name

        if alert.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == alert.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.ACKNOWLEDGED
                inc.acknowledged_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_ACKNOWLEDGED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value, "assigned_volunteer": alert.assigned_volunteer_name},
            channel="medical"
        )
        return alert

    @staticmethod
    async def dispatch_medical_unit(
        db: AsyncSession,
        alert_id: str,
        resource_id: str,
        volunteer_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert = (await db.execute(select(MedicalAlert).where(MedicalAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            raise NotFoundException("Medical alert not found")

        resource = (await db.execute(select(Resource).where(Resource.id == resource_id))).scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        alert.status = MedicalAlertStatus.DISPATCHED
        alert.assigned_resource_id = resource_id
        if volunteer_name:
            alert.assigned_volunteer_name = volunteer_name

        # Update resource status
        resource.availability = ResourceAvailability.ASSIGNED

        # Create assignment
        assignment = ResourceAssignment(
            resource_id=resource.id,
            incident_id=alert.incident_id,
            assigned_by=user_id,
            status=ResourceAssignmentStatus.EN_ROUTE,
            notes=f"Dispatched for medical alert {alert.alert_code}"
        )
        db.add(assignment)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_UNIT_DISPATCHED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id,
            new_value={"resource_code": resource.resource_code, "volunteer": volunteer_name}
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value, "resource_code": resource.resource_code},
            channel="medical"
        )
        return alert

    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        alert_id: str,
        resolution_notes: str,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert = (await db.execute(select(MedicalAlert).where(MedicalAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            raise NotFoundException("Medical alert not found")

        alert.status = MedicalAlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)

        if alert.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == alert.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.RESOLVED
                inc.resolved_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_RESOLVED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value},
            channel="medical"
        )
        return alert

    @staticmethod
    async def get_alerts(db: AsyncSession, status: Optional[MedicalAlertStatus] = None) -> List[MedicalAlert]:
        query = select(MedicalAlert).order_by(MedicalAlert.created_at.desc())
        if status:
            query = query.where(MedicalAlert.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())


medical_service = MedicalService()
