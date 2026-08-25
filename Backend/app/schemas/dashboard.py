from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    active_incidents: int
    active_lost_person_cases: int
    active_medical_alerts: int
    critical_zones: int
    deployed_resources: int
    available_resources: int
    active_cameras: int
    total_cameras: int
    estimated_pilgrim_count: int
    max_crowd_density: float
    palkhi_location: str
    palkhi_status: str
    last_updated: datetime


class IncidentTickerItem(BaseModel):
    timestamp: str
    formatted_text: str
    incident_number: Optional[str] = None
    type: str
    severity: str


class HeatRiskReadout(BaseModel):
    ambient_temperature: str = "34° C"
    relative_humidity: str = "72%"
    computed_risk_index: str = "7.8 / 10 (MODERATE HEAT RISK)"
    water_stations_active: str = "12 Operational"
    orsl_sachet_supplies: str = "14,200 Packets Available"
    advisory_action: str = "Trigger mist sprayer vans at Wakhri Junction & increase water distribution post deployment by 20%."


class CorridorRouteSegment(BaseModel):
    name: str
    sector: str
    density_percentage: float
    color_hex: str
    status_tag: str
    coordinates: List[List[float]]
