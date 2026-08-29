import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.announcement import AnnouncementStatus, PublicAnnouncement
from app.schemas.announcement import AnnouncementCreate, AnnouncementOut
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.announcements")


class AnnouncementService:
    @staticmethod
    async def create_announcement(
        db: AsyncSession,
        ann_in: AnnouncementCreate,
        user_id: Optional[str] = None
    ) -> PublicAnnouncement:
        ann = PublicAnnouncement(
            message_mr=ann_in.message_mr,
            message_en=ann_in.message_en,
            target_zone_id=ann_in.target_zone_id,
            category=ann_in.category,
            priority=ann_in.priority,
            status=AnnouncementStatus.PENDING_APPROVAL,
            requested_by=user_id
        )
        db.add(ann)
        await db.commit()
        await db.refresh(ann)

        await ws_manager.broadcast(
            WebSocketEventType.ANNOUNCEMENT_CREATED,
            {"id": ann.id, "message_mr": ann.message_mr, "priority": ann.priority},
            channel="dashboard"
        )
        return ann

    @staticmethod
    async def approve_and_broadcast(
        db: AsyncSession,
        announcement_id: str,
        approver_id: Optional[str] = None
    ) -> PublicAnnouncement:
        query = select(PublicAnnouncement).where(PublicAnnouncement.id == announcement_id)
        ann = (await db.execute(query)).scalars().first()
        if not ann:
            raise ValueError("Announcement not found")

        now = datetime.now(timezone.utc)
        ann.status = AnnouncementStatus.BROADCAST
        ann.approved_by = approver_id
        ann.broadcast_at = now
        await db.commit()
        await db.refresh(ann)

        await ws_manager.broadcast(
            WebSocketEventType.ANNOUNCEMENT_BROADCAST,
            {
                "id": ann.id,
                "message_mr": ann.message_mr,
                "message_en": ann.message_en,
                "broadcast_at": now.isoformat()
            },
            channel="all"
        )
        return ann

    @staticmethod
    async def list_announcements(db: AsyncSession, limit: int = 20) -> List[PublicAnnouncement]:
        query = select(PublicAnnouncement).order_by(desc(PublicAnnouncement.created_at)).limit(limit)
        return list((await db.execute(query)).scalars().all())


announcement_service = AnnouncementService()
