import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ActionType(str, enum.Enum):
    ACKNOWLEDGE_INCIDENT = "ACKNOWLEDGE_INCIDENT"
    ASSIGN_INCIDENT = "ASSIGN_INCIDENT"
    DISPATCH_POLICE = "DISPATCH_POLICE"
    DISPATCH_VOLUNTEER = "DISPATCH_VOLUNTEER"
    DISPATCH_AMBULANCE = "DISPATCH_AMBULANCE"
    DISPATCH_MEDICAL_VAN = "DISPATCH_MEDICAL_VAN"
    DISPATCH_WATER_TANKER = "DISPATCH_WATER_TANKER"
    CHANGE_RESOURCE_STATUS = "CHANGE_RESOURCE_STATUS"
    REASSIGN_RESOURCE = "REASSIGN_RESOURCE"
    CHANGE_ROUTE = "CHANGE_ROUTE"
    QUEUE_PA_ANNOUNCEMENT = "QUEUE_PA_ANNOUNCEMENT"
    BROADCAST_PUBLIC_ALERT = "BROADCAST_PUBLIC_ALERT"
    VERIFY_FACE_MATCH = "VERIFY_FACE_MATCH"
    REUNITE_LOST_PERSON = "REUNITE_LOST_PERSON"
    RESOLVE_INCIDENT = "RESOLVE_INCIDENT"
    CLOSE_INCIDENT = "CLOSE_INCIDENT"


class ActionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CommandAction(BaseModel):
    __tablename__ = "command_actions"

    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_types"),
        nullable=False,
        index=True
    )
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # RESOURCE, ROUTE, LOST_PERSON, INCIDENT, ANNOUNCEMENT
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    requested_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="action_statuses"),
        default=ActionStatus.PROPOSED,
        nullable=False,
        index=True
    )
    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
