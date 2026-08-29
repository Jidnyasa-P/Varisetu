from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.resource import ResourceAvailability, ResourceType, ResourceAssignmentStatus


class ResourceBase(BaseModel):
    resource_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    resource_type: ResourceType
    capacity: Optional[int] = None
    status_tag: str = "OPTIMAL"
    availability: ResourceAvailability = ResourceAvailability.AVAILABLE
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    zone_id: Optional[str] = None
    location_description: Optional[str] = None
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    status_tag: Optional[str] = None
    availability: Optional[ResourceAvailability] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    zone_id: Optional[str] = None
    location_description: Optional[str] = None
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None


class ResourceStatusUpdateRequest(BaseModel):
    availability: ResourceAvailability
    status_tag: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class ResourceDispatchRequest(BaseModel):
    incident_id: Optional[str] = None
    target_location: Optional[str] = None
    notes: Optional[str] = None


class ResourceAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    resource_id: str
    incident_id: Optional[str] = None
    status: ResourceAssignmentStatus
    assigned_at: datetime
    accepted_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    distance_km: Optional[float] = None
    assignments: Optional[List[ResourceAssignmentOut]] = None
