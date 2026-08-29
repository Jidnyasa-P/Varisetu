from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity, IncidentStatus, IncidentType


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    description: Optional[str] = None
    zone_id: Optional[str] = None
    camera_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    source: str = "OPERATOR"


class IncidentCreate(IncidentBase):
    is_demo: bool = False


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    description: Optional[str] = None
    assigned_user_id: Optional[str] = None


class IncidentAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class IncidentResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=2)


class IncidentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    event_type: str
    message: str
    actor_user_id: Optional[str] = None
    metadata_json: Optional[dict] = None
    created_at: datetime


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_number: str
    status: IncidentStatus
    created_by: Optional[str] = None
    assigned_user_id: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    events: Optional[List[IncidentEventOut]] = None
