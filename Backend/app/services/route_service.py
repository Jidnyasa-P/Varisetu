from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException
from app.models.incident import Incident, IncidentEvent
from app.models.route import Route, RouteStatus
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class RouteService:
    @staticmethod
    async def get_routes(db: AsyncSession) -> List[Route]:
        query = select(Route).order_by(Route.priority, Route.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def change_status(
        db: AsyncSession,
        route_id: str,
        status: RouteStatus,
        reason: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Route:
        query = select(Route).where(Route.id == route_id)
        result = await db.execute(query)
        route = result.scalar_one_or_none()

        if not route:
            raise NotFoundException("Route corridor not found")

        old_status = route.status.value
        route.status = status
        route.updated_by = user_id

        await audit_service.log_action(
            db=db,
            action="ROUTE_STATUS_CHANGED",
            entity_type="Route",
            entity_id=route.id,
            user_id=user_id,
            old_value={"status": old_status},
            new_value={"status": status.value, "reason": reason}
        )

        await db.commit()
        await db.refresh(route)

        # Broadcast update
        await ws_manager.broadcast(
            WebSocketEventType.ROUTE_CHANGED,
            {"route_id": route.id, "name": route.name, "status": route.status.value, "reason": reason},
            channel="dashboard"
        )
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] Route {route.name} status updated: {route.status.value}"},
            channel="dashboard"
        )
        return route


route_service = RouteService()
