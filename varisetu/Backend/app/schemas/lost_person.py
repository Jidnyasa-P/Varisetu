from datetime import datetime
from typing import List, Optional
import json
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.face_match import FaceMatchStatus
from app.models.lost_person import LostPersonStatus


class LostPersonReportBase(BaseModel):
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    transcript: Optional[str] = None
    language: str = "mr"
    asr_confidence: Optional[float] = None


class LostPersonReportCreate(LostPersonReportBase):
    pass


class LostPersonReportOut(LostPersonReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    audio_file_url: Optional[str] = None
    reported_at: datetime


class FaceMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    camera_id: Optional[str] = None
    frame_reference: Optional[str] = None
    similarity_score: float
    confidence: float
    status: FaceMatchStatus
    detected_at: datetime
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class LostPersonCaseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., description="M / F / Other")
    clothing_description: str = Field(..., min_length=2)
    physical_description: Optional[str] = None
    last_seen_location: str = Field(..., min_length=2)
    last_seen_camera_id: Optional[str] = None
    photo_url: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    priority: str = "HIGH"

    @field_validator('photo_urls', mode='before')
    @classmethod
    def parse_photo_urls(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [v]
            except Exception:
                return [v]
        return [str(v)]


class LostPersonCaseCreate(LostPersonCaseBase):
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    initial_transcript: Optional[str] = None
    is_demo: bool = False


class LostPersonCaseUpdate(BaseModel):
    clothing_description: Optional[str] = None
    physical_description: Optional[str] = None
    status: Optional[LostPersonStatus] = None
    last_seen_location: Optional[str] = None


class LostPersonCaseOut(LostPersonCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    incident_id: Optional[str] = None
    status: LostPersonStatus
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    reports: Optional[List[LostPersonReportOut]] = None
    matches: Optional[List[FaceMatchOut]] = None


class FaceMatchVerifyRequest(BaseModel):
    verified: bool = True
    officer_notes: Optional[str] = None
    notes: Optional[str] = None


class PurgeSensitiveDataResponse(BaseModel):
    success: bool
    message: str
    purged_records_count: int
    case_id: str
