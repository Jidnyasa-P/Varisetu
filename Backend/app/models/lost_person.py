import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class LostPersonStatus(str, enum.Enum):
    SEARCHING = "SEARCHING"
    MATCH_FOUND = "MATCH_FOUND"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    REUNITED = "REUNITED"
    CLOSED = "CLOSED"


class LostPersonCase(BaseModel):
    __tablename__ = "lost_person_cases"

    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    clothing_description: Mapped[str] = mapped_column(Text, nullable=False)
    physical_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_seen_location: Mapped[str] = mapped_column(String(150), nullable=False)
    last_seen_camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    photo_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    status: Mapped[LostPersonStatus] = mapped_column(
        Enum(LostPersonStatus, name="lost_person_statuses"),
        default=LostPersonStatus.SEARCHING,
        nullable=False,
        index=True
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships with selectin loading
    reports = relationship("LostPersonReport", back_populates="case", cascade="all, delete-orphan", lazy="selectin")
    matches = relationship("FaceMatchResult", back_populates="case", cascade="all, delete-orphan", lazy="selectin")
    camera = relationship("Camera", backref="lost_persons", lazy="selectin")


class LostPersonReport(BaseModel):
    __tablename__ = "lost_person_reports"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("lost_person_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    caller_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    caller_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    audio_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="mr", nullable=False)
    asr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("LostPersonCase", back_populates="reports")
