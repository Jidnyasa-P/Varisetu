import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class YatraStatus(str, enum.Enum):
    LIVE = "LIVE"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    OFFLINE = "OFFLINE"


class Yatra(BaseModel):
    __tablename__ = "yatras"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="PALKHI", nullable=False)
    status: Mapped[YatraStatus] = mapped_column(
        Enum(YatraStatus, name="yatra_statuses"),
        default=YatraStatus.LIVE,
        nullable=False
    )
    current_latitude: Mapped[float] = mapped_column(Float, default=17.7280, nullable=False)
    current_longitude: Mapped[float] = mapped_column(Float, default=75.2950, nullable=False)
    current_speed: Mapped[float] = mapped_column(Float, default=2.8, nullable=False)
    current_heading: Mapped[float] = mapped_column(Float, default=145.0, nullable=False)
    current_accuracy: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    last_gps_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    current_zone_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    current_route_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    active_tracker_id: Mapped[Optional[str]] = mapped_column(String(50), default="PALKHI-TUKARAM-01", nullable=True)


class YatraTrack(BaseModel):
    __tablename__ = "yatra_tracks"

    yatra_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    tracker_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_meters: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    speed_kmph: Mapped[float] = mapped_column(Float, default=2.8, nullable=False)
    heading: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    altitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="GPS_DEVICE", nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_snapped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
