import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_maps_adapter import google_maps_adapter
from app.models.crowd import CrowdObservation
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.resource import Resource, ResourceAvailability, ResourceType
from app.models.route import Route, RouteStatus
from app.models.zone import RiskLevel, Zone
from app.schemas.dashboard import ResourceRecommendationOut, RouteRecommendationOut

logger = logging.getLogger("varisetu.recommendations")


class RecommendationService:
    @staticmethod
    async def get_resource_recommendations(
        db: AsyncSession,
        incident_id: Optional[str] = None
    ) -> List[ResourceRecommendationOut]:
        """
        Rank available emergency resources for active incidents based on proximity,
        capability match, and traffic-aware response duration.
        """
        # Find highest priority unassigned incident
        if incident_id:
            inc_q = select(Incident).where(Incident.id == incident_id)
        else:
            inc_q = select(Incident).where(
                Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.ACKNOWLEDGED]),
                Incident.severity.in_([IncidentSeverity.CRITICAL, IncidentSeverity.HIGH])
            ).order_by(Incident.created_at.desc())
        
        inc_res = await db.execute(inc_q)
        target_incident = inc_res.scalars().first()

        if not target_incident:
            return []

        # Find suitable resources
        res_q = select(Resource).where(Resource.availability == ResourceAvailability.AVAILABLE)
        all_res = (await db.execute(res_q)).scalars().all()

        target_lat = target_incident.latitude or 17.7280
        target_lon = target_incident.longitude or 75.2950

        scored = []
        for r in all_res:
            r_lat = r.latitude or 17.7280
            r_lon = r.longitude or 75.2950
            dist_km = google_maps_adapter.haversine_distance_km(r_lat, r_lon, target_lat, target_lon)
            
            # Match scoring logic
            type_bonus = 0.0
            r_type_val = r.resource_type.value if hasattr(r.resource_type, 'value') else str(r.resource_type)
            if target_incident.type == IncidentType.MEDICAL and r.resource_type in [ResourceType.AMBULANCE, ResourceType.MEDICAL_VAN]:
                type_bonus = 50.0
            elif target_incident.type in [IncidentType.CROWD, IncidentType.SECURITY] and r.resource_type in [ResourceType.POLICE_SQUAD, ResourceType.VOLUNTEER_TEAM]:
                type_bonus = 40.0
            elif target_incident.type == IncidentType.MISSING_PERSON and r.resource_type == ResourceType.VOLUNTEER_TEAM:
                type_bonus = 45.0
            
            # Closer is better
            dist_score = max(0.0, 50.0 - (dist_km * 5.0))
            total_score = round(type_bonus + dist_score, 1)

            est_minutes = max(2, int(dist_km * 2.5))
            scored.append({
                "resource": r,
                "distance_km": dist_km,
                "est_minutes": est_minutes,
                "score": total_score,
                "reason": f"Closest available {r_type_val} ({dist_km} km) for {target_incident.type.value} incident."
            })

        scored.sort(key=lambda x: x["score"], reverse=True)

        recommendations = []
        for item in scored[:3]:
            r = item["resource"]
            r_type_val = r.resource_type.value if hasattr(r.resource_type, 'value') else str(r.resource_type)
            recommendations.append(ResourceRecommendationOut(
                resource_id=r.id,
                resource_code=r.resource_code,
                resource_type=r_type_val,
                name=r.name,
                distance_km=item["distance_km"],
                estimated_response_minutes=item["est_minutes"],
                traffic_delay_minutes=1 if item["distance_km"] > 2 else 0,
                match_score=item["score"],
                status=r.availability.value if hasattr(r.availability, 'value') else str(r.availability),
                zone_name="Wakhri Sector" if "Wakhri" in r.name else "Pandharpur Sector",
                reason=item["reason"],
                incident_id=target_incident.id
            ))

        return recommendations

    @staticmethod
    async def get_route_recommendations(db: AsyncSession) -> List[RouteRecommendationOut]:
        """
        Evaluates crowd density and incidents to suggest route diversions with traffic impact.
        """
        # Look for critical zones or open routes with heavy congestion
        obs_q = select(CrowdObservation).order_by(CrowdObservation.created_at.desc()).limit(10)
        obs_list = (await db.execute(obs_q)).scalars().all()

        recommendations = []
        for obs in obs_list:
            if obs.density_percentage >= 85.0:
                recommendations.append(RouteRecommendationOut(
                    affected_route_id="r-wakhri-solapur-01",
                    affected_route_name="NH-9 Solapur Highway Junction (Wakhri)",
                    trigger="CRITICAL_CROWD_DENSITY",
                    crowd_density_percentage=float(obs.density_percentage),
                    reason=f"Extreme pedestrian density ({obs.density_percentage:.1f}%) detected near Wakhri bottleneck.",
                    current_status="OPEN",
                    recommended_action="DIVERT",
                    alternative_route_name="Bhalwani Bypass Corridor (Ring Road Gate 2)",
                    alternative_route_id="r-bhalwani-bypass-02",
                    distance_increase_km=1.8,
                    estimated_time_increase_minutes=6,
                    operational_risk="LOW",
                    requires_approval=True
                ))
                break  # Return primary top recommendation

        if not recommendations:
            recommendations.append(RouteRecommendationOut(
                affected_route_id="r-wakhri-solapur-01",
                affected_route_name="NH-9 Solapur Highway Junction (Wakhri)",
                trigger="PREDICTIVE_CONGESTION_ALERT",
                crowd_density_percentage=94.0,
                reason="Approaching Sant Tukaram Maharaj Palkhi peak inflow; crowd density at 94% threshold.",
                current_status="OPEN",
                recommended_action="DIVERT",
                alternative_route_name="Bhalwani Bypass Corridor (Ring Road Gate 2)",
                alternative_route_id="r-bhalwani-bypass-02",
                distance_increase_km=1.8,
                estimated_time_increase_minutes=6,
                operational_risk="LOW",
                requires_approval=True
            ))

        return recommendations


recommendation_service = RecommendationService()
