from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.zone import Zone
from app.schemas.crowd import CrowdForecastPoint, CrowdForecastResponse, ZoneForecastData


class ForecastService:
    @staticmethod
    async def get_2hour_forecast(db: AsyncSession) -> CrowdForecastResponse:
        """
        Generate 2-hour congestion forecast model (7 intervals from 19:00 to 21:00 IST).
        Deterministic rule-based forecast baseline version.
        """
        time_labels = ["19:00 IST", "19:20 IST", "19:40 IST", "20:00 IST", "20:20 IST", "20:40 IST", "21:00 IST"]

        # Default prediction profiles matching the operational dashboard
        profiles = {
            "Pandharpur Chowk": [94.0, 96.0, 98.0, 92.0, 85.0, 78.0, 70.0],
            "Wakhri Phata": [88.0, 90.0, 86.0, 82.0, 75.0, 68.0, 60.0]
        }

        zones_data: List[ZoneForecastData] = []
        for zone_name, densities in profiles.items():
            pts = []
            for t_label, d_val in zip(time_labels, densities):
                risk = "CRITICAL" if d_val >= 90 else ("HIGH" if d_val >= 75 else "MODERATE")
                pts.append(CrowdForecastPoint(
                    timestamp=t_label,
                    predicted_density=d_val,
                    risk_level=risk
                ))
            zones_data.append(ZoneForecastData(zone_name=zone_name, forecast_points=pts))

        return CrowdForecastResponse(
            time_labels=time_labels,
            zones=zones_data,
            model_version="demo-rule-based-v1",
            generated_at=datetime.now(timezone.utc)
        )


forecast_service = ForecastService()
