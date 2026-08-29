from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.schemas.audit import AuditLogOut
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.demo_service import demo_service

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"], dependencies=[Depends(get_current_user)])
audit_router = APIRouter(prefix="/audit", tags=["Audit"], dependencies=[Depends(get_current_user)])
demo_router = APIRouter(prefix="/demo", tags=["Demo"], dependencies=[Depends(get_current_user)])
health_router = APIRouter(tags=["Health"])


# --- NOTIFICATIONS ENDPOINTS ---
@notifications_router.get("", response_model=List[NotificationOut], summary="List notifications")
async def list_notifications(limit: int = 50, db: AsyncSession = Depends(get_db)):
    query = select(Notification).order_by(desc(Notification.created_at)).limit(limit)
    result = await db.execute(query)
    return [NotificationOut.model_validate(n) for n in result.scalars().all()]


@notifications_router.post("", response_model=NotificationOut, status_code=status.HTTP_201_CREATED, summary="Create notification")
async def create_notification(notif_in: NotificationCreate, db: AsyncSession = Depends(get_db)):
    notif = Notification(**notif_in.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return NotificationOut.model_validate(notif)


@notifications_router.patch("/{id}/read", response_model=NotificationOut, summary="Mark notification as read")
async def mark_notification_read(id: str, db: AsyncSession = Depends(get_db)):
    notif = (await db.execute(select(Notification).where(Notification.id == id))).scalar_one_or_none()
    if not notif:
        raise NotFoundException("Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return NotificationOut.model_validate(notif)


# --- AUDIT ENDPOINTS ---
@audit_router.get("", response_model=List[AuditLogOut], summary="Query operational audit logs")
async def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at))
    if action:
        query = query.where(AuditLog.action == action)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    query = query.limit(limit)
    result = await db.execute(query)
    return [AuditLogOut.model_validate(a) for a in result.scalars().all()]


# --- DEMO SIMULATION ENDPOINTS ---
@demo_router.post("/start", summary="Start automated Wari pilgrimage operational simulation")
async def start_demo_simulation():
    """Launches an asynchronous realistic operational emergency flow."""
    return await demo_service.start()


@demo_router.post("/stop", summary="Stop automated demo simulation")
async def stop_demo_simulation():
    """Cancels the active demo simulation."""
    return await demo_service.stop()


@demo_router.get("/status", summary="Get demo simulation status")
async def get_demo_status():
    """Check whether demo simulation is currently running and current step index."""
    return demo_service.get_status()


# --- HEALTH CHECK ENDPOINTS (PUBLIC) ---
@health_router.get("/health", summary="Basic health check")
async def health_check():
    return {"status": "ok", "service": "varisetu-backend", "version": "2.0.0"}


@health_router.get("/health/database", summary="Database health check")
async def health_database(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "connected", "database": "healthy"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@health_router.get("/health/redis", summary="Redis health check")
async def health_redis():
    from app.core.redis import redis_client
    return {
        "status": "connected" if redis_client.is_connected else "fallback_in_memory",
        "redis_available": redis_client.is_connected
    }


@health_router.get("/health/services", summary="Integration services status check")
async def health_services():
    from app.core.config import settings
    from app.integrations.qdrant_adapter import qdrant_adapter
    return {
        "database": "postgresql_compatible",
        "redis": "ready",
        "qdrant": await qdrant_adapter.health_check(),
        "speech": settings.SPEECH_PROVIDER,
        "vision": settings.VISION_PROVIDER,
        "weather": settings.WEATHER_PROVIDER,
        "notifications": settings.NOTIFICATION_PROVIDER
    }
