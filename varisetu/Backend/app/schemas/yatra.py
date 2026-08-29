from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.yatra import YatraStatus


class YatraTrackPointInput(BaseModel):
    tracker_id: str = Field(..., min_length=2, max_length=50)
    yatra_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    speed_kmph: Optional[float] = Field(default=2.8, ge=0.0, le=120.0)
    heading: Optional[float] = Field(default=0.0, ge=0.0, le=360.0)
    accuracy_meters: Optional[float] = Field(default=5.0, ge=0.0, le=500.0)
    altitude: Optional[float] = None
    source: str = "GPS_DEVICE"
    sequence_number: Optional[int] = 0


class YatraTrackPointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    yatra_id: str
    tracker_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    accuracy_meters: float
    speed_kmph: float
    heading: float
    altitude: Optional[float] = None
    source: str
    sequence_number: int
    is_snapped: bool


class YatraCheckpointOut(BaseModel):
    id: str
    name: str
    marathi_name: str
    latitude: float
    longitude: float
    sequence: int
    zone_id: Optional[str] = None
    distance_km_from_start: float
    is_reached: bool = False
    eta_minutes: Optional[int] = None


class YatraLiveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    type: str
    status: YatraStatus
    latitude: float
    longitude: float
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    speed_kmph: float
    current_speed: Optional[float] = None
    heading: float
    current_heading: Optional[float] = None
    accuracy_meters: float
    current_accuracy: Optional[float] = None
    last_gps_update: datetime
    current_zone_id: Optional[str] = None
    current_route_id: Optional[str] = None
    active_tracker_id: Optional[str] = None
    data_age_seconds: int = 0
    current_checkpoint: Optional[str] = None
    next_checkpoint: Optional[str] = None
    distance_remaining_km: float = 0.0
    eta_to_pandharpur_minutes: int = 0
    recent_track: Optional[List[YatraTrackPointOut]] = None


class PublicYatraOut(BaseModel):
    name: str
    approximate_latitude: float
    approximate_longitude: float
    route_name: str
    current_location_name: str
    status: str
    speed_kmph: float
    last_update: str
    public_advisory: str
