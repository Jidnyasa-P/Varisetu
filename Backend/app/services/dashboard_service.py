from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select

from app.integrations.weather_adapter import weather_adapter
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation
from app.models.incident import Incident, IncidentEvent, IncidentStatus
from app.models.lost_person import LostPersonCase, LostPersonStatus
from app.models.medical import MedicalAlert, MedicalAlertStatus
from app.models.resource import Resource, ResourceAvailability
from app.models.zone import RiskLevel, Zone
from app.schemas.dashboard import DashboardSummary, HeatRiskReadout, IncidentTickerItem


class DashboardService:
    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        # Active incidents count
        inc_q = select(func.count(Incident.id)).where(Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED]))
        active_inc = (await db.execute(inc_q)).scalar() or 0

        # Active lost person cases count
        lost_q = select(func.count(LostPersonCase.id)).where(LostPersonCase.status.notin_([LostPersonStatus.REUNITED, LostPersonStatus.CLOSED]))
        active_lost = (await db.execute(lost_q)).scalar() or 0

        # Active medical alerts count
        med_q = select(func.count(MedicalAlert.id)).where(MedicalAlert.status.notin_([MedicalAlertStatus.RESOLVED, MedicalAlertStatus.CLOSED]))
        active_med = (await db.execute(med_q)).scalar() or 0

        # Critical zones count
        crit_q = select(func.count(Zone.id)).where(Zone.risk_level == RiskLevel.CRITICAL)
        crit_zones = (await db.execute(crit_q)).scalar() or 0

        # Deployed vs Available resources
        dep_q = select(func.count(Resource.id)).where(Resource.availability.in_([ResourceAvailability.ASSIGNED, ResourceAvailability.EN_ROUTE, ResourceAvailability.ON_SCENE]))
        avail_q = select(func.count(Resource.id)).where(Resource.availability == ResourceAvailability.AVAILABLE)
        total_res_q = select(func.count(Resource.id))
        deployed_res = (await db.execute(dep_q)).scalar() or 0
        avail_res = (await db.execute(avail_q)).scalar() or 0
        total_res = (await db.execute(total_res_q)).scalar() or (deployed_res + avail_res)

        # Cameras count
        cam_online_q = select(func.count(Camera.id)).where(Camera.status == CameraStatus.ONLINE)
        cam_total_q = select(func.count(Camera.id))
        active_cams = (await db.execute(cam_online_q)).scalar() or 0
        total_cams = (await db.execute(cam_total_q)).scalar() or 0

        # Max crowd density from latest observations
        max_density_q = select(func.max(CrowdObservation.density_percentage))
        max_density = (await db.execute(max_density_q)).scalar() or 94.0

        return DashboardSummary(
            active_incidents=active_inc,
            active_lost_person_cases=active_lost,
            active_medical_alerts=active_med,
            critical_zones=crit_zones,
            deployed_resources=deployed_res,
            available_resources=avail_res,
            total_resources=total_res,
            active_cameras=active_cams,
            total_cameras=total_cams,
            estimated_pilgrim_count=845000,
            max_crowd_density=float(max_density),
            max_density=float(max_density),
            palkhi_location="Approaching Wakhri Phata (Km 184)",
            palkhi_status="Sant Tukaram Maharaj Palkhi",
            last_updated=datetime.now(timezone.utc)
        )

    @staticmethod
    async def get_ticker_events(db: AsyncSession, limit: int = 20) -> List[IncidentTickerItem]:
        query = select(IncidentEvent).order_by(desc(IncidentEvent.created_at)).limit(limit)
        events = (await db.execute(query)).scalars().all()

        ticker_items = []
        for ev in events:
            time_str = ev.created_at.strftime("%H:%M:%S")
            ticker_items.append(IncidentTickerItem(
                timestamp=time_str,
                formatted_text=f"[{time_str}] {ev.message}",
                type=ev.event_type,
                severity="NORMAL"
            ))

        # If no events yet in DB, return standard initial events
        if not ticker_items:
            now_str = datetime.now().strftime("%H:%M:%S")
            return [
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] CAM-12 Wakhri Phata: Density peak detected (88%)",
                    type="CROWD_PEAK",
                    severity="HIGH"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Medical alert raised at Sector 4: Pilgrim fainting, Ambulance MH-12-PA-4022 dispatched",
                    type="MEDICAL_ALERT",
                    severity="CRITICAL"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Lost Person Case #LF-802: Facial match confidence 89% on CAM-04",
                    type="LOST_PERSON_MATCH",
                    severity="HIGH"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Solapur Highway Diversion Gate 2 opened",
                    type="ROUTE_DIVERTED",
                    severity="NORMAL"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Water tanker #WT-09 refilled at Wakhri Station",
                    type="RESOURCE_OPTIMAL",
                    severity="LOW"
                )
            ]

        return ticker_items

    @staticmethod
    async def get_heat_risk() -> HeatRiskReadout:
        data = await weather_adapter.get_heat_metrics(17.7280, 75.2950)
        return HeatRiskReadout(**data)


dashboard_service = DashboardService()
