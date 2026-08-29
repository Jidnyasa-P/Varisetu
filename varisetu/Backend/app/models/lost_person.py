import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CallState(str, enum.Enum):
    IDLE = "IDLE"
    REQUESTING_MICROPHONE = "REQUESTING_MICROPHONE"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    LISTENING = "LISTENING"
    SPEAKING = "SPEAKING"
    SILENCE_DETECTED = "SILENCE_DETECTED"
    PROCESSING_UTTERANCE = "PROCESSING_UTTERANCE"
    TRANSLATING = "TRANSLATING"
    OPERATOR_HOLD = "OPERATOR_HOLD"
    RECONNECTING = "RECONNECTING"
    PROVIDER_DEGRADED = "PROVIDER_DEGRADED"
    CALL_ENDING = "CALL_ENDING"
    CALL_ENDED = "CALL_ENDED"
    ERROR = "ERROR"


class LostPersonStatus(str, enum.Enum):
    SEARCHING = "SEARCHING"
    MATCH_FOUND = "MATCH_FOUND"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    REUNITED = "REUNITED"
    CLOSED = "CLOSED"


class CallSession(BaseModel):
    __tablename__ = "call_sessions"

    session_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    caller_name: Mapped[Optional[str]] = mapped_column(String(100), default="Citizen Caller", nullable=True)
    caller_phone: Mapped[Optional[str]] = mapped_column(String(30), default="+91-112", nullable=True)
    dialed_line: Mapped[str] = mapped_column(String(50), default="112 Helpline", nullable=False)
    source_language: Mapped[str] = mapped_column(String(20), default="mr", nullable=False)
    call_state: Mapped[CallState] = mapped_column(
        Enum(CallState, name="call_states"),
        default=CallState.IDLE,
        nullable=False,
        index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hold_duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    operator_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    operator_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    audio_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    native_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    english_translation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asr_provider: Mapped[str] = mapped_column(String(50), default="sarvam", nullable=False)
    translation_provider: Mapped[str] = mapped_column(String(50), default="sarvam", nullable=False)
    asr_confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.95, nullable=True)
    translation_confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.92, nullable=True)
    extracted_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    transcript_segments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


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
    call_session_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    caller_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    caller_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    audio_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    english_translation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="mr", nullable=False)
    asr_provider: Mapped[str] = mapped_column(String(50), default="sarvam", nullable=False)
    translation_provider: Mapped[str] = mapped_column(String(50), default="sarvam", nullable=False)
    asr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    translation_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extracted_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("LostPersonCase", back_populates="reports")
