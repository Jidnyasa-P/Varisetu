import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"


class Camera(BaseModel):
    __tablename__ = "cameras"

    camera_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    rtsp_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[CameraStatus] = mapped_column(
        Enum(CameraStatus, name="camera_statuses"),
        default=CameraStatus.ONLINE,
        nullable=False,
        index=True
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    zone = relationship("Zone", backref="cameras")
