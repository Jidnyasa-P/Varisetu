from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.camera import CameraStatus


class CameraBase(BaseModel):
    camera_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    zone_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    rtsp_url: Optional[str] = None
    status: CameraStatus = CameraStatus.ONLINE


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    rtsp_url: Optional[str] = None
    status: Optional[CameraStatus] = None


class CameraHeartbeat(BaseModel):
    status: CameraStatus = CameraStatus.ONLINE
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CameraPTZCommand(BaseModel):
    action: str = Field(..., description="pan_left, pan_right, tilt_up, tilt_down, zoom_in, zoom_out, preset")
    value: Optional[float] = None
    preset_id: Optional[int] = None


class CameraOut(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    current_density: Optional[float] = None
    density_status: Optional[str] = None
