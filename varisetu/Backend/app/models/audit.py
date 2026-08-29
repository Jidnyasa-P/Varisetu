from typing import Optional
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # LOGIN, INCIDENT_ACKNOWLEDGED, DISPATCH, etc.
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Incident, MedicalAlert, Route, etc.
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
