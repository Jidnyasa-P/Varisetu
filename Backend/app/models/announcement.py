import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AnnouncementStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    QUEUED = "QUEUED"
    BROADCAST = "BROADCAST"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PublicAnnouncement(BaseModel):
    __tablename__ = "public_announcements"

    message_mr: Mapped[str] = mapped_column(Text, nullable=False)
    message_en: Mapped[str] = mapped_column(Text, nullable=False)
    target_zone_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="CROWD_SAFETY", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    status: Mapped[AnnouncementStatus] = mapped_column(
        Enum(AnnouncementStatus, name="announcement_statuses"),
        default=AnnouncementStatus.PENDING_APPROVAL,
        nullable=False,
        index=True
    )
    requested_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    broadcast_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
