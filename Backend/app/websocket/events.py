import enum
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class WebSocketEventType(str, enum.Enum):
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_UPDATED = "INCIDENT_UPDATED"
    CROWD_UPDATED = "CROWD_UPDATED"
    MEDICAL_ALERT_CREATED = "MEDICAL_ALERT_CREATED"
    MEDICAL_ALERT_UPDATED = "MEDICAL_ALERT_UPDATED"
    RESOURCE_DISPATCHED = "RESOURCE_DISPATCHED"
    RESOURCE_STATUS_CHANGED = "RESOURCE_STATUS_CHANGED"
    LOST_PERSON_MATCH_FOUND = "LOST_PERSON_MATCH_FOUND"
    LOST_PERSON_VERIFIED = "LOST_PERSON_VERIFIED"
    LOST_PERSON_REUNITED = "LOST_PERSON_REUNITED"
    ROUTE_CHANGED = "ROUTE_CHANGED"
    TICKER_EVENT = "TICKER_EVENT"
    SYSTEM_ALERT = "SYSTEM_ALERT"


class WebSocketMessage(BaseModel):
    event: WebSocketEventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Dict[str, Any]
