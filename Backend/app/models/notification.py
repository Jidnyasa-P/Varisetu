import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    INCIDENT = "INCIDENT"
    MEDICAL = "MEDICAL"
    CROWD = "CROWD"
    LOST_PERSON = "LOST_PERSON"
    RESOURCE = "RESOURCE"
    SYSTEM = "SYSTEM"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_types"),
        default=NotificationType.SYSTEM,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
