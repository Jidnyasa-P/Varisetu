import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ResourceType(str, enum.Enum):
    WATER_TANKER = "WATER_TANKER"
    MEDICAL_VAN = "MEDICAL_VAN"
    POLICE_SQUAD = "POLICE_SQUAD"
    VOLUNTEER_TEAM = "VOLUNTEER_TEAM"
    FOOD_VAN = "FOOD_VAN"
    AMBULANCE = "AMBULANCE"
    OTHER = "OTHER"


class ResourceAvailability(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    UNAVAILABLE = "UNAVAILABLE"
    OFFLINE = "OFFLINE"


class ResourceAssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Resource(BaseModel):
    __tablename__ = "resources"

    resource_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="resource_types"),
        nullable=False,
        index=True
    )
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status_tag: Mapped[str] = mapped_column(String(50), default="OPTIMAL", nullable=False)
    availability: Mapped[ResourceAvailability] = mapped_column(
        Enum(ResourceAvailability, name="resource_availabilities"),
        default=ResourceAvailability.AVAILABLE,
        nullable=False,
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    location_description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    operator_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operator_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships with selectin loading
    zone = relationship("Zone", backref="resources", lazy="selectin")
    assignments = relationship("ResourceAssignment", back_populates="resource", cascade="all, delete-orphan", lazy="selectin")


class ResourceAssignment(BaseModel):
    __tablename__ = "resource_assignments"

    resource_id: Mapped[str] = mapped_column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[ResourceAssignmentStatus] = mapped_column(
        Enum(ResourceAssignmentStatus, name="assignment_statuses"),
        default=ResourceAssignmentStatus.PENDING,
        nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    arrived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    resource = relationship("Resource", back_populates="assignments")
