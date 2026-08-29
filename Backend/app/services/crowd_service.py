from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.zone import RiskLevel, Zone
from app.schemas.crowd import CrowdObservationCreate
from app.schemas.zone import ZoneCrowdMetrics
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class CrowdService:
    @staticmethod
    def calculate_risk(density: float) -> RiskLevel:
        if density >= 90.0:
            return RiskLevel.CRITICAL
        elif density >= 75.0:
            return RiskLevel.HIGH
        elif density >= 55.0:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    @staticmethod
    def get_recommended_action(zone_name: str, density: float) -> str:
        if "Pandharpur" in zone_name and density >= 90:
            return "Divert pilgrim queue via North Ring Road"
        elif "Wakhri" in zone_name and density >= 80:
            return "Deploy 4 extra police constables to junction"
        elif "Vakhri" in zone_name and density >= 70:
            return "Monitor bottleneck near bridge entry"
        elif "Saswad" in zone_name:
            return "Normal traffic regulation"
        elif "Tarapur" in zone_name:
            return "Allow local supply vehicle passage"
        return "Standard patrol active"

    @staticmethod
    async def record_observation(db: AsyncSession, obs_in: CrowdObservationCreate) -> CrowdObservation:
        risk = CrowdService.calculate_risk(obs_in.density_percentage)
        obs = CrowdObservation(
            zone_id=obs_in.zone_id,
            camera_id=obs_in.camera_id,
            density_percentage=obs_in.density_percentage,
            people_count=obs_in.people_count,
            movement_direction=obs_in.movement_direction,
            trend=obs_in.trend,
            risk_level=risk,
            source=obs_in.source,
            observed_at=obs_in.observed_at or datetime.now(timezone.utc)
        )
        db.add(obs)

        # Update Zone current risk level
        zone = (await db.execute(select(Zone).where(Zone.id == obs_in.zone_id))).scalar_one_or_none()
        if zone:
            zone.risk_level = risk

        await db.commit()
        await db.refresh(obs)

        await ws_manager.broadcast(
            WebSocketEventType.CROWD_UPDATED,
            {
                "zone_id": obs.zone_id,
                "density_percentage": obs.density_percentage,
                "trend": obs.trend.value,
                "risk_level": obs.risk_level.value
            },
            channel="crowd"
        )
        return obs

    @staticmethod
    async def get_current_zone_metrics(db: AsyncSession) -> List[ZoneCrowdMetrics]:
        zones = (await db.execute(select(Zone).where(Zone.is_active == True))).scalars().all()
        metrics = []

        for z in zones:
            # Fetch latest observation
            obs_q = select(CrowdObservation).where(CrowdObservation.zone_id == z.id).order_by(desc(CrowdObservation.observed_at)).limit(1)
            obs = (await db.execute(obs_q)).scalar_one_or_none()

            density = obs.density_percentage if obs else 40.0
            people_cnt = obs.people_count if obs else 500
            trend_val = obs.trend.value if obs else "STABLE"
            risk = obs.risk_level if obs else z.risk_level
            last_up = obs.observed_at if obs else z.updated_at

            metrics.append(ZoneCrowdMetrics(
                zone_id=z.id,
                zone_name=z.name,
                density_percentage=density,
                people_count=people_cnt,
                trend=trend_val,
                risk_level=risk,
                recommended_action=CrowdService.get_recommended_action(z.name, density),
                last_updated=last_up
            ))

        # Sort by density descending
        metrics.sort(key=lambda m: m.density_percentage, reverse=True)
        return metrics


crowd_service = CrowdService()
