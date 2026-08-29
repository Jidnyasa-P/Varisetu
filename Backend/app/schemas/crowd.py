from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.crowd import CrowdTrend
from app.models.zone import RiskLevel


class CrowdObservationCreate(BaseModel):
    zone_id: str
    camera_id: Optional[str] = None
    density_percentage: float = Field(..., ge=0.0, le=100.0)
    people_count: int = Field(default=0, ge=0)
    movement_direction: Optional[str] = None
    trend: CrowdTrend = CrowdTrend.STABLE
    risk_level: RiskLevel = RiskLevel.LOW
    source: str = "DEMO"
    observed_at: Optional[datetime] = None


class CrowdObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zone_id: str
    camera_id: Optional[str] = None
    density_percentage: float
    people_count: int
    movement_direction: Optional[str] = None
    trend: CrowdTrend
    risk_level: RiskLevel
    source: str
    observed_at: datetime
    created_at: datetime


class CrowdForecastPoint(BaseModel):
    timestamp: str
    predicted_density: float
    risk_level: str


class ZoneForecastData(BaseModel):
    zone_name: str
    forecast_points: List[CrowdForecastPoint]


class CrowdForecastResponse(BaseModel):
    time_labels: List[str]
    zones: List[ZoneForecastData]
    model_version: str = "demo-rule-based-v1"
    generated_at: datetime
