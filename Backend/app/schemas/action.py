from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.action import ActionStatus, ActionType


class ActionBase(BaseModel):
    action_type: ActionType
    incident_id: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    priority: str = "HIGH"
    parameters: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class ActionCreate(ActionBase):
    idempotency_key: Optional[str] = None


class ActionApproveRequest(BaseModel):
    notes: Optional[str] = None


class ActionOut(ActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    status: ActionStatus
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
