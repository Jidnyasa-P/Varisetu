from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.announcement import AnnouncementStatus


class AnnouncementBase(BaseModel):
    message_mr: str = Field(..., min_length=2)
    message_en: str = Field(..., min_length=2)
    target_zone_id: Optional[str] = None
    category: str = "CROWD_SAFETY"
    priority: str = "HIGH"


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementApproveRequest(BaseModel):
    notes: Optional[str] = None


class AnnouncementOut(AnnouncementBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: AnnouncementStatus
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    broadcast_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
