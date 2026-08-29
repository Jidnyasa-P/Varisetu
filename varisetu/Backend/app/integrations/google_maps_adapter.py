import logging
import math
import os
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("varisetu.google_maps")


class GoogleMapsAdapter:
    """
    Adapter for Google Maps Platform:
    - Google Routes API (traffic-aware routes, alternatives, ETAs)
    - Google Roads API (snap-to-road, path interpolation)
    - Fallback deterministic offline simulator when keys are absent or network is down.
    """

    def __init__(self):
        self.server_api_key = getattr(settings, "GOOGLE_MAPS_SERVER_API_KEY", None) or os.getenv("GOOGLE_MAPS_SERVER_API_KEY")
        self.is_enabled = bool(self.server_api_key)

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two GPS coordinates."""
        r = 6371.0  # Earth radius km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 2)

    async def snap_to_roads(self, points: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Snap a sequence of GPS coordinates to the likely road network.
        Falls back to raw coordinates if API key is missing or call fails.
        """
        if not self.is_enabled or len(points) < 2:
            return [{"latitude": p["latitude"], "longitude": p["longitude"], "is_snapped": False} for p in points]

        try:
            path_param = "|".join(f"{p['latitude']},{p['longitude']}" for p in points[:100])
            url = f"https://roads.googleapis.com/v1/snapToRoads?path={path_param}&interpolate=true&key={self.server_api_key}"
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    snapped = res.json().get("snappedPoints", [])
                    return [
                        {
                            "latitude": item["location"]["latitude"],
                            "longitude": item["location"]["longitude"],
                            "is_snapped": True,
                            "original_index": item.get("originalIndex")
                        }
                        for item in snapped
                    ]
        except Exception as e:
            logger.warning(f"Google Roads API snap failed, using raw coordinates fallback: {e}")

        return [{"latitude": p["latitude"], "longitude": p["longitude"], "is_snapped": False} for p in points]

    async def compute_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        travel_mode: str = "DRIVE",
        routing_preference: str = "TRAFFIC_AWARE"
    ) -> Dict[str, Any]:
        """
        Calculates traffic-aware duration and distance using Google Routes API.
        Falls back to haversine + speed model if offline.
        """
        dist_km = self.haversine_distance_km(origin_lat, origin_lon, dest_lat, dest_lon)
        # Default fallback calculation (assuming average 30 km/h emergency speed in pilgrimage corridor)
        est_minutes = max(1, int((dist_km / 30.0) * 60.0))

        if not self.is_enabled:
            return {
                "distance_km": dist_km,
                "duration_minutes": est_minutes,
                "traffic_duration_minutes": est_minutes + (2 if dist_km > 2 else 0),
                "source": "INTERNAL_FALLBACK"
            }

        try:
            url = "https://routes.googleapis.com/directions/v2:computeRoutes"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.server_api_key,
                "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.staticDuration"
            }
            body = {
                "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lon}}},
                "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lon}}},
                "travelMode": travel_mode,
                "routingPreference": routing_preference
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, json=body, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    route = data["routes"][0]
                    dist_meters = route.get("distanceMeters", dist_km * 1000)
                    dur_str = route.get("duration", f"{est_minutes * 60}s")
                    dur_sec = int(dur_str.rstrip("s")) if dur_str.endswith("s") else est_minutes * 60
                    return {
                        "distance_km": round(dist_meters / 1000.0, 2),
                        "duration_minutes": max(1, dur_sec // 60),
                        "traffic_duration_minutes": max(1, dur_sec // 60),
                        "source": "GOOGLE_ROUTES_API"
                    }
        except Exception as e:
            logger.warning(f"Google Routes API call failed, using fallback: {e}")

        return {
            "distance_km": dist_km,
            "duration_minutes": est_minutes,
            "traffic_duration_minutes": est_minutes + (2 if dist_km > 2 else 0),
            "source": "INTERNAL_FALLBACK"
        }


google_maps_adapter = GoogleMapsAdapter()
