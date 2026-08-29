import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.zone import RiskLevel


class CrowdTrend(str, enum.Enum):
    RISING = "RISING"
    STABLE = "STABLE"
    FALLING = "FALLING"
    EASING = "EASING"


class CrowdObservation(BaseModel):
    __tablename__ = "crowd_observations"

    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True, index=True)
    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    density_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    movement_direction: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    trend: Mapped[CrowdTrend] = mapped_column(
        Enum(CrowdTrend, name="crowd_trends"),
        default=CrowdTrend.STABLE,
        nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="crowd_risk_levels"),
        default=RiskLevel.LOW,
        nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), default="DEMO", nullable=False)  # DEMO / VISION_YOLO / SENSOR
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    zone = relationship("Zone", backref="crowd_observations")
    camera = relationship("Camera", backref="crowd_observations")


# Composite index for performance
Index("idx_crowd_zone_time", CrowdObservation.zone_id, CrowdObservation.observed_at.desc())
