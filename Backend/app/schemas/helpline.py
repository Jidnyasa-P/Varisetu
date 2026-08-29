import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.lost_person import CallState
from app.models.face_match import MatchType, FaceMatchStatus
from app.schemas.lost_person import LostPersonCaseOut


class TranscriptSegment(BaseModel):
    id: str = Field(..., description="Unique segment identifier (e.g. seg_001)")
    start_ms: int = Field(0, description="Start offset in milliseconds from call start")
    end_ms: int = Field(0, description="End offset in milliseconds")
    language: str = Field("mr", description="Language code: mr, hi, en")
    native_text: str = Field(..., description="Recognized speech in native script")
    english_text: Optional[str] = Field(None, description="Contextual English translation")
    is_final: bool = Field(False, description="Whether this utterance is finalized")
    asr_confidence: float = Field(0.95, description="ASR model confidence score")
    translation_confidence: float = Field(0.92, description="Translation confidence score")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExtractedMissingPersonAttributes(BaseModel):
    name: Optional[str] = Field(None, description="Missing person name in English / Devanagari")
    age: Optional[int] = Field(None, description="Estimated age")
    gender: Optional[str] = Field(None, description="M, F, or OTHER")
    clothing_description: Optional[str] = Field(None, description="Description of garments worn")
    physical_description: Optional[str] = Field(None, description="Height, build, complexion, hair")
    accessories: Optional[str] = Field(None, description="Tulsi mala, cymbals, stick, bag, cap")
    last_seen_location: Optional[str] = Field(None, description="Specific corridor, ghat, or landmark")
    last_seen_time: Optional[str] = Field(None, description="Time last seen")
    direction_of_travel: Optional[str] = Field(None, description="Heading towards temple, dindi, etc.")
    companions: Optional[str] = Field(None, description="Family or Dindi group details")
    special_identifiers: Optional[str] = Field(None, description="Scars, marks, ribbons, medical needs")
    urgency: Optional[str] = Field("HIGH", description="LOW, MEDIUM, HIGH, CRITICAL")
    confidence: Dict[str, float] = Field(default_factory=dict, description="Field-level confidence mapping")


class CallInitRequest(BaseModel):
    caller_name: Optional[str] = Field("Citizen Caller", description="Name of the caller if known")
    caller_phone: Optional[str] = Field("+91-112", description="Caller phone number")
    dialed_line: Optional[str] = Field("112 Emergency Helpline", description="Line dialed")
    language: Optional[str] = Field("mr", description="Preferred initial language")
    is_demo: bool = Field(False, description="Whether this is a demo simulation session")


class CallSessionOut(BaseModel):
    session_id: str
    caller_name: str
    caller_phone: str
    dialed_line: str
    source_language: str
    call_state: CallState
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: int = 0
    hold_duration_seconds: int = 0
    native_transcript: Optional[str] = ""
    english_translation: Optional[str] = ""
    asr_provider: str = "sarvam"
    translation_provider: str = "sarvam"
    asr_confidence: float = 0.95
    translation_confidence: float = 0.92
    extracted_attributes: Dict[str, Any] = Field(default_factory=dict)
    transcript_segments: List[TranscriptSegment] = Field(default_factory=list)
    audio_file_url: Optional[str] = None
    is_demo: bool = False


class CallActionResponse(BaseModel):
    session_id: str
    call_state: CallState
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UpdateOperatorReportRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    clothing_description: Optional[str] = None
    physical_description: Optional[str] = None
    accessories: Optional[str] = None
    last_seen_location: Optional[str] = None
    urgency: Optional[str] = None
    notes: Optional[str] = None


class CreateCaseFromSessionRequest(BaseModel):
    name: str
    age: int
    gender: str = "M"
    clothing_description: str
    last_seen_location: str
    physical_description: Optional[str] = None
    urgency: Optional[str] = "HIGH"
    zone_id: Optional[str] = None
    trigger_cctv_scan: bool = True
    reporter_notes: Optional[str] = None


class CCTVScanCandidate(BaseModel):
    match_id: str
    case_id: str
    camera_id: Optional[str] = None
    camera_code: str
    camera_name: str
    location_name: str
    latitude: float
    longitude: float
    similarity_score: float
    confidence: float
    confidence_label: str
    match_type: MatchType
    status: FaceMatchStatus
    frame_timestamp: str
    matched_features: str
    snapshot_url: str
    tracking_id: Optional[str] = None
    source: str = "VISION_ENGINE"


class CCTVScanResponse(BaseModel):
    success: bool
    case_id: str
    case_number: str
    search_window_minutes: int
    cameras_searched_count: int
    candidates_count: int
    candidates: List[CCTVScanCandidate]
    message: str


class CreateCaseFromSessionResponse(BaseModel):
    case: LostPersonCaseOut
    report_id: str
    call_session_id: str
    cctv_candidates: List[CCTVScanCandidate]
    message: str


class HelplineScenarioOut(BaseModel):
    id: str
    title: str
    caller_phone: str
    caller_name: str
    dialed_line: str
    language: str
    language_name: str


class CallSimulationRequest(BaseModel):
    scenario_id: Optional[str] = None
    custom_text: Optional[str] = None
    language: Optional[str] = "mr"


class CallSimulationResponse(BaseModel):
    session_id: str
    scenario_id: Optional[str]
    title: str
    caller_phone: str
    caller_name: str
    dialed_line: str
    language: str
    language_name: str
    native_transcript: str
    english_translation: str
    confidence: float
    extracted_attributes: Dict[str, Any]
    waveform: List[int]
    timestamp: str
    source: str = "DEMO"
