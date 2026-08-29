from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.zone import RiskLevel


class CrowdForecast(BaseModel):
    __tablename__ = "crowd_forecasts"

    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    predicted_density: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="forecast_risk_levels"),
        default=RiskLevel.LOW,
        nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(50), default="demo-rule-based-v1", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)

    # Relationship
    zone = relationship("Zone", backref="forecasts")
