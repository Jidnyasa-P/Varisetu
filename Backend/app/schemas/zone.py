from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.zone import RiskLevel


class ZoneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    capacity: int = Field(default=50000, ge=1)
    risk_level: RiskLevel = RiskLevel.LOW
    is_active: bool = True


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    capacity: Optional[int] = Field(None, ge=1)
    risk_level: Optional[RiskLevel] = None
    is_active: Optional[bool] = None


class ZoneOut(ZoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ZoneCrowdMetrics(BaseModel):
    zone_id: str
    zone_name: str
    density_percentage: float
    people_count: int
    trend: str
    risk_level: RiskLevel
    recommended_action: str
    last_updated: datetime
