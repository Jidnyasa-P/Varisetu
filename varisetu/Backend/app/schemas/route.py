from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.route import RouteStatus


class RouteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    status: RouteStatus = RouteStatus.OPEN
    priority: str = "PRIMARY"
    latitude_start: Optional[float] = None
    longitude_start: Optional[float] = None
    latitude_end: Optional[float] = None
    longitude_end: Optional[float] = None


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[RouteStatus] = None
    priority: Optional[str] = None


class RouteActionRequest(BaseModel):
    reason: Optional[str] = None


class RouteOut(RouteBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
