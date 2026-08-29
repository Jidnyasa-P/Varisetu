from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.action import ActionOut
from app.schemas.camera import CameraOut
from app.schemas.incident import IncidentEventOut, IncidentOut
from app.schemas.lost_person import FaceMatchOut, LostPersonCaseOut
from app.schemas.medical import MedicalAlertOut
from app.schemas.notification import NotificationOut
from app.schemas.resource import ResourceOut
from app.schemas.route import RouteOut
from app.schemas.yatra import YatraLiveOut
from app.schemas.zone import ZoneOut


class DashboardSummary(BaseModel):
    active_incidents: int
    active_lost_person_cases: int
    active_medical_alerts: int
    critical_zones: int
    deployed_resources: int
    available_resources: int
    total_resources: int
    active_cameras: int
    total_cameras: int
    estimated_pilgrim_count: int
    max_crowd_density: float
    max_density: float
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


class DataFreshnessMetrics(BaseModel):
    data_age_seconds: int = 2
    camera_telemetry_age_seconds: int = 1
    gps_age_seconds: int = 3
    weather_age_seconds: int = 28
    gis_provider: str = "GOOGLE_MAPS"
    gis_provider_status: str = "LIVE"
    last_sync_timestamp: str


class ResourceRecommendationOut(BaseModel):
    resource_id: str
    resource_code: str
    resource_type: str
    name: str
    distance_km: float
    estimated_response_minutes: int
    traffic_delay_minutes: int = 0
    match_score: float
    status: str
    zone_name: Optional[str] = None
    reason: str
    incident_id: Optional[str] = None


class RouteRecommendationOut(BaseModel):
    affected_route_id: str
    affected_route_name: str
    trigger: str
    crowd_density_percentage: float
    reason: str
    current_status: str
    recommended_action: str  # DIVERT, CLOSE, RESTRICT_VEHICLES
    alternative_route_name: str
    alternative_route_id: Optional[str] = None
    distance_increase_km: float
    estimated_time_increase_minutes: int
    operational_risk: str
    requires_approval: bool = True
    incident_id: Optional[str] = None


class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    weight: float
    density_percentage: float
    estimated_count: int
    source: str
    zone_id: Optional[str] = None
    timestamp: str
    risk_level: str


class CommandPictureOut(BaseModel):
    generated_at: str
    system_health: Dict[str, str]
    summary: DashboardSummary
    freshness: DataFreshnessMetrics
    yatra: Optional[YatraLiveOut] = None
    critical_incidents: List[IncidentOut] = []
    active_incidents: List[IncidentOut] = []
    active_medical_alerts: List[MedicalAlertOut] = []
    active_lost_cases: List[LostPersonCaseOut] = []
    face_match_candidates: List[FaceMatchOut] = []
    deployed_resources: List[ResourceOut] = []
    available_resources: List[ResourceOut] = []
    routes: List[RouteOut] = []
    corridor_segments: List[CorridorRouteSegment] = []
    route_recommendations: List[RouteRecommendationOut] = []
    resource_recommendations: List[ResourceRecommendationOut] = []
    recent_actions: List[ActionOut] = []
    incident_timeline: List[IncidentEventOut] = []
    unread_notifications: List[NotificationOut] = []
    heatmap_points: List[HeatmapPoint] = []
