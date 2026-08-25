import enum
from typing import Optional
from sqlalchemy import Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RouteStatus(str, enum.Enum):
    OPEN = "OPEN"
    DIVERTED = "DIVERTED"
    CLOSED = "CLOSED"
    EMERGENCY_ACCESS = "EMERGENCY_ACCESS"
    PILGRIMS_ONLY = "PILGRIMS_ONLY"


class Route(BaseModel):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[RouteStatus] = mapped_column(
        Enum(RouteStatus, name="route_statuses"),
        default=RouteStatus.OPEN,
        nullable=False,
        index=True
    )
    priority: Mapped[str] = mapped_column(String(20), default="PRIMARY", nullable=False)
    latitude_start: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude_start: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latitude_end: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude_end: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
