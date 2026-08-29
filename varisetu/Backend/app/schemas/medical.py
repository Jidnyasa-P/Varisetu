from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity
from app.models.medical import MedicalAlertStatus, MedicalAlertType


class MedicalAlertBase(BaseModel):
    type: MedicalAlertType
    severity: IncidentSeverity = IncidentSeverity.HIGH
    zone_id: Optional[str] = None
    camera_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    description: str = Field(..., min_length=2)
    assigned_volunteer_name: Optional[str] = None


class MedicalAlertCreate(MedicalAlertBase):
    is_demo: bool = False


class MedicalAlertAcknowledgeRequest(BaseModel):
    assigned_volunteer_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalAlertDispatchRequest(BaseModel):
    resource_id: str
    volunteer_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalAlertResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=2)


class MedicalAlertOut(MedicalAlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_code: str
    incident_id: Optional[str] = None
    status: MedicalAlertStatus
    assigned_resource_id: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
