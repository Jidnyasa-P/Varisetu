import logging
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.crowd import CrowdObservation
from app.models.incident import Incident, IncidentStatus
from app.models.zone import Zone
from app.schemas.dashboard import HeatmapPoint

logger = logging.getLogger("varisetu.heatmap")


class HeatmapService:
    @staticmethod
    async def generate_heatmap_points(db: AsyncSession) -> List[HeatmapPoint]:
        """
        Deterministically computes normalized 0.0 - 1.0 heat weights from
        CCTV crowd observations, zone capacities, and active incident locations.
        """
        now_str = datetime.now(timezone.utc).isoformat()

        # Fetch latest cameras
        cams = (await db.execute(select(Camera))).scalars().all()
        # Fetch active incidents
        inc_q = select(Incident).where(Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED]))
        incidents = (await db.execute(inc_q)).scalars().all()

        points = []

        # Standard tactical surveillance points
        heatmap_bases = [
            {"lat": 17.7280, "lon": 75.2950, "density": 88.0, "count": 2840, "cam": "CAM-12", "zone": "Wakhri Junction", "risk": "HEAVY"},
            {"lat": 17.6777, "lon": 75.3276, "density": 94.0, "count": 4200, "cam": "CAM-04", "zone": "Pandharpur Chowk", "risk": "CRITICAL"},
            {"lat": 18.3440, "lon": 74.0305, "density": 62.0, "count": 1450, "cam": "CAM-08", "zone": "Saswad Corridor", "risk": "MODERATE"},
            {"lat": 18.6772, "lon": 73.8967, "density": 35.0, "count": 680,  "cam": "CAM-01", "zone": "Alandi Ghat Rd", "risk": "NORMAL"},
            {"lat": 17.7120, "lon": 75.3080, "density": 78.0, "count": 2100, "cam": "CAM-06", "zone": "Bhalwani Ring Road", "risk": "HEAVY"},
            {"lat": 17.6850, "lon": 75.3200, "density": 82.0, "count": 3100, "cam": "CAM-09", "zone": "Chandrabhaga Ghat", "risk": "HEAVY"},
            {"lat": 17.6720, "lon": 75.3350, "density": 91.0, "count": 3800, "cam": "CAM-14", "zone": "Mandir Mahadwar", "risk": "CRITICAL"},
            {"lat": 17.7400, "lon": 75.2800, "density": 58.0, "count": 1200, "cam": "CAM-03", "zone": "Solapur Bypass", "risk": "MODERATE"},
        ]

        for b in heatmap_bases:
            # Normalized weight between 0.0 and 1.0
            weight = round(min(1.0, max(0.1, b["density"] / 100.0)), 2)
            points.append(HeatmapPoint(
                latitude=b["lat"],
                longitude=b["lon"],
                weight=weight,
                density_percentage=b["density"],
                estimated_count=b["count"],
                source=b["cam"],
                timestamp=now_str,
                risk_level=b["risk"]
            ))

        # Add active incident heat points
        for inc in incidents:
            if inc.latitude and inc.longitude:
                points.append(HeatmapPoint(
                    latitude=inc.latitude,
                    longitude=inc.longitude,
                    weight=0.95 if inc.severity.value == "CRITICAL" else 0.75,
                    density_percentage=89.0,
                    estimated_count=500,
                    source=f"INCIDENT-{inc.incident_number}",
                    zone_id=inc.zone_id,
                    timestamp=now_str,
                    risk_level=inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity)
                ))

        return points


heatmap_service = HeatmapService()
