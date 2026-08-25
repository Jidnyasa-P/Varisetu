import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.incident import IncidentSeverity


class MedicalAlertType(str, enum.Enum):
    FALL = "FALL"
    FAINTING = "FAINTING"
    HEAT_EXHAUSTION = "HEAT_EXHAUSTION"
    DEHYDRATION = "DEHYDRATION"
    CARDIAC_RISK = "CARDIAC_RISK"
    OTHER = "OTHER"


class MedicalAlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class MedicalAlert(BaseModel):
    __tablename__ = "medical_alerts"

    alert_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[MedicalAlertType] = mapped_column(
        Enum(MedicalAlertType, name="medical_alert_types"),
        nullable=False,
        index=True
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="medical_severities"),
        default=IncidentSeverity.HIGH,
        nullable=False
    )
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MedicalAlertStatus] = mapped_column(
        Enum(MedicalAlertStatus, name="medical_alert_statuses"),
        default=MedicalAlertStatus.ACTIVE,
        nullable=False,
        index=True
    )
    assigned_resource_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("resources.id", ondelete="SET NULL"), nullable=True)
    assigned_volunteer_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    zone = relationship("Zone", backref="medical_alerts")
    camera = relationship("Camera", backref="medical_alerts")
    resource = relationship("Resource", backref="assigned_medical_alerts", foreign_keys=[assigned_resource_id])
