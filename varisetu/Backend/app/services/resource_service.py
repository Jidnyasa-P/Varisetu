import math
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.incident import Incident, IncidentEvent
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability, ResourceType
from app.schemas.resource import ResourceOut
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class ResourceService:
    @staticmethod
    async def get_resources(
        db: AsyncSession,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None
    ) -> List[Resource]:
        query = select(Resource).options(selectinload(Resource.assignments)).order_by(Resource.resource_code)
        if resource_type:
            query = query.where(Resource.resource_type == resource_type)
        if availability:
            query = query.where(Resource.availability == availability)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_nearby_resources(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None,
        limit: int = 10
    ) -> List[ResourceOut]:
        resources = await ResourceService.get_resources(db, resource_type, availability)
        result_items = []
        for r in resources:
            dist = haversine_distance(latitude, longitude, r.latitude, r.longitude)
            out_model = ResourceOut.model_validate(r)
            out_model.distance_km = dist
            result_items.append(out_model)

        # Sort by proximity
        result_items.sort(key=lambda x: x.distance_km or 999999.0)
        return result_items[:limit]

    @staticmethod
    async def dispatch_resource(
        db: AsyncSession,
        resource_id: str,
        incident_id: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Resource:
        query = select(Resource).where(Resource.id == resource_id).options(selectinload(Resource.assignments))
        result = await db.execute(query)
        resource = result.scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        resource.availability = ResourceAvailability.ASSIGNED

        assignment = ResourceAssignment(
            resource_id=resource.id,
            incident_id=incident_id,
            assigned_by=user_id,
            status=ResourceAssignmentStatus.EN_ROUTE,
            notes=notes
        )
        db.add(assignment)

        if incident_id:
            event = IncidentEvent(
                incident_id=incident_id,
                event_type="RESOURCE_DISPATCHED",
                message=f"Resource {resource.name} ({resource.resource_code}) dispatched to incident scene.",
                actor_user_id=user_id
            )
            db.add(event)

        await audit_service.log_action(
            db=db,
            action="RESOURCE_DISPATCHED",
            entity_type="Resource",
            entity_id=resource.id,
            user_id=user_id,
            new_value={"availability": resource.availability.value, "incident_id": incident_id}
        )

        await db.commit()
        await db.refresh(resource)

        await ws_manager.broadcast(
            WebSocketEventType.RESOURCE_DISPATCHED,
            {"resource_id": resource.id, "resource_code": resource.resource_code, "status": resource.availability.value},
            channel="resources"
        )
        return resource

    @staticmethod
    async def update_status(
        db: AsyncSession,
        resource_id: str,
        availability: ResourceAvailability,
        status_tag: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> Resource:
        resource = (await db.execute(select(Resource).where(Resource.id == resource_id))).scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        old_val = {"availability": resource.availability.value}
        resource.availability = availability
        if status_tag:
            resource.status_tag = status_tag
        if latitude is not None:
            resource.latitude = latitude
        if longitude is not None:
            resource.longitude = longitude

        await audit_service.log_action(
            db=db,
            action="RESOURCE_STATUS_UPDATED",
            entity_type="Resource",
            entity_id=resource.id,
            user_id=user_id,
            old_value=old_val,
            new_value={"availability": availability.value}
        )

        await db.commit()
        await db.refresh(resource)

        await ws_manager.broadcast(
            WebSocketEventType.RESOURCE_STATUS_CHANGED,
            {"resource_id": resource.id, "availability": resource.availability.value},
            channel="resources"
        )
        return resource


resource_service = ResourceService()
