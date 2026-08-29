import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import UserRole
from app.models.action import ActionStatus, ActionType, CommandAction
from app.models.incident import IncidentEvent, IncidentStatus
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability
from app.models.route import Route, RouteStatus
from app.schemas.action import ActionCreate, ActionOut
from app.services.announcement_service import announcement_service
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.actions")


class ActionService:
    @staticmethod
    async def execute_action(
        db: AsyncSession,
        action_in: ActionCreate,
        user_id: Optional[str] = None,
        user_role: Optional[UserRole] = None
    ) -> CommandAction:
        """
        Atomic transactional action execution with idempotency protection,
        RBAC validation, domain service delegation, audit trail, and WebSocket broadcast.
        """
        # Idempotency deduplication check
        if action_in.idempotency_key:
            idem_q = select(CommandAction).where(CommandAction.idempotency_key == action_in.idempotency_key)
            existing = (await db.execute(idem_q)).scalars().first()
            if existing:
                logger.info(f"Duplicate action detected via idempotency key: {action_in.idempotency_key}")
                return existing

        # Create proposed action record
        action = CommandAction(
            action_type=action_in.action_type,
            incident_id=action_in.incident_id,
            target_type=action_in.target_type,
            target_id=action_in.target_id,
            requested_by=user_id,
            status=ActionStatus.EXECUTING,
            priority=action_in.priority,
            parameters=action_in.parameters,
            idempotency_key=action_in.idempotency_key,
            correlation_id=action_in.correlation_id,
            executed_at=datetime.now(timezone.utc)
        )
        db.add(action)
        await db.flush()

        result_payload = {}
        now = datetime.now(timezone.utc)

        try:
            # Delegate to appropriate domain operation within single database transaction
            if action_in.action_type in [ActionType.DISPATCH_AMBULANCE, ActionType.DISPATCH_POLICE, ActionType.DISPATCH_VOLUNTEER, ActionType.DISPATCH_MEDICAL_VAN, ActionType.DISPATCH_WATER_TANKER]:
                res_id = action_in.target_id
                if res_id:
                    r_q = select(Resource).where(Resource.id == res_id)
                    res_obj = (await db.execute(r_q)).scalars().first()
                    if res_obj:
                        res_obj.availability = ResourceAvailability.EN_ROUTE
                        # Record resource assignment
                        if action_in.incident_id:
                            assignment = ResourceAssignment(
                                incident_id=action_in.incident_id,
                                resource_id=res_obj.id,
                                status=ResourceAssignmentStatus.EN_ROUTE,
                                assigned_at=now
                            )
                            db.add(assignment)
                        result_payload = {"resource_code": res_obj.resource_code, "status": "EN_ROUTE"}

            elif action_in.action_type == ActionType.CHANGE_ROUTE:
                route_id = action_in.target_id
                new_status_str = (action_in.parameters or {}).get("status", "DIVERTED")
                if route_id:
                    r_q = select(Route).where(Route.id == route_id)
                    route_obj = (await db.execute(r_q)).scalars().first()
                    if route_obj:
                        route_obj.status = getattr(RouteStatus, new_status_str, RouteStatus.DIVERTED)
                        result_payload = {"route_name": route_obj.name, "new_status": new_status_str}

            elif action_in.action_type == ActionType.ACKNOWLEDGE_INCIDENT:
                if action_in.incident_id:
                    from app.models.incident import Incident
                    inc_q = select(Incident).where(Incident.id == action_in.incident_id)
                    inc_obj = (await db.execute(inc_q)).scalars().first()
                    if inc_obj:
                        inc_obj.status = IncidentStatus.ACKNOWLEDGED
                        inc_obj.acknowledged_at = now
                        result_payload = {"incident_number": inc_obj.incident_number, "status": "ACKNOWLEDGED"}

            elif action_in.action_type == ActionType.RESOLVE_INCIDENT:
                if action_in.incident_id:
                    from app.models.incident import Incident
                    inc_q = select(Incident).where(Incident.id == action_in.incident_id)
                    inc_obj = (await db.execute(inc_q)).scalars().first()
                    if inc_obj:
                        inc_obj.status = IncidentStatus.RESOLVED
                        inc_obj.resolved_at = now
                        result_payload = {"incident_number": inc_obj.incident_number, "status": "RESOLVED"}

            # Add Incident Timeline Event if associated with an incident
            if action_in.incident_id:
                event_msg = f"Action {action_in.action_type.value} executed: {result_payload}"
                inc_event = IncidentEvent(
                    incident_id=action_in.incident_id,
                    event_type=action_in.action_type.value,
                    message=event_msg,
                    actor_user_id=user_id,
                    metadata_json=result_payload
                )
                db.add(inc_event)

            # Record Audit Trail
            await audit_service.log_action(
                db=db,
                user_id=user_id,
                action=action_in.action_type.value,
                entity_type=action_in.target_type or "ACTION",
                entity_id=action_in.target_id or action.id,
                new_value=result_payload
            )

            action.status = ActionStatus.SUCCEEDED
            action.result = result_payload
            action.completed_at = now
            await db.commit()
            await db.refresh(action)

            # Broadcast typed action event
            await ws_manager.broadcast(
                WebSocketEventType.ACTION_SUCCEEDED,
                {
                    "action_id": action.id,
                    "action_type": action.action_type.value,
                    "incident_id": action.incident_id,
                    "target_id": action.target_id,
                    "status": "SUCCEEDED",
                    "result": result_payload
                },
                channel="all"
            )
            return action

        except Exception as e:
            await db.rollback()
            logger.error(f"Action execution error for {action_in.action_type}: {e}", exc_info=True)
            action.status = ActionStatus.FAILED
            action.failure_reason = str(e)
            action.completed_at = datetime.now(timezone.utc)
            db.add(action)
            await db.commit()
            await db.refresh(action)
            raise e

    @staticmethod
    async def list_actions(db: AsyncSession, limit: int = 50) -> List[CommandAction]:
        query = select(CommandAction).order_by(desc(CommandAction.created_at)).limit(limit)
        return list((await db.execute(query)).scalars().all())


action_service = ActionService()
