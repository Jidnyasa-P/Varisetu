from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationType


class NotificationCreate(BaseModel):
    user_id: Optional[str] = None
    incident_id: Optional[str] = None
    type: NotificationType = NotificationType.SYSTEM
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2)
    priority: str = "NORMAL"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    incident_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
