import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class FaceMatchStatus(str, enum.Enum):
    CANDIDATE = "CANDIDATE"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class FaceMatchResult(BaseModel):
    __tablename__ = "face_match_results"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("lost_person_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    frame_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    status: Mapped[FaceMatchStatus] = mapped_column(
        Enum(FaceMatchStatus, name="face_match_statuses"),
        default=FaceMatchStatus.CANDIDATE,
        nullable=False
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    verified_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("LostPersonCase", back_populates="matches")
    camera = relationship("Camera", backref="face_matches")
