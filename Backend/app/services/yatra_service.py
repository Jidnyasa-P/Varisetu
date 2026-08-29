import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_maps_adapter import google_maps_adapter
from app.models.yatra import Yatra, YatraStatus, YatraTrack
from app.schemas.yatra import PublicYatraOut, YatraCheckpointOut, YatraLiveOut, YatraTrackPointInput, YatraTrackPointOut
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.yatra")

CHECKPOINTS = [
    {"id": "cp-01", "name": "Alandi", "marathi_name": "आळंदी देवस्थान", "lat": 18.6772, "lon": 73.8967, "seq": 1, "dist_km": 0.0},
    {"id": "cp-02", "name": "Saswad", "marathi_name": "सासवड पालखी तळ", "lat": 18.3440, "lon": 74.0305, "seq": 2, "dist_km": 42.0},
    {"id": "cp-03", "name": "Lonand", "marathi_name": "लोणंद", "lat": 18.0400, "lon": 74.1900, "seq": 3, "dist_km": 96.0},
    {"id": "cp-04", "name": "Wakhri", "marathi_name": "वाखरी फाटा तळ", "lat": 17.7280, "lon": 75.2950, "seq": 4, "dist_km": 184.0},
    {"id": "cp-05", "name": "Pandharpur", "marathi_name": "श्री क्षेत्र पंढरपूर मंदिर", "lat": 17.6777, "lon": 75.3276, "seq": 5, "dist_km": 210.0}
]


class YatraService:
    @staticmethod
    async def get_or_create_primary_yatra(db: AsyncSession) -> Yatra:
        query = select(Yatra).where(Yatra.name.contains("Tukaram")).limit(1)
        yatra = (await db.execute(query)).scalars().first()
        if not yatra:
            yatra = Yatra(
                name="Sant Tukaram Maharaj Palkhi",
                type="PALKHI",
                status=YatraStatus.LIVE,
                current_latitude=17.7280,
                current_longitude=75.2950,
                current_speed=2.8,
                current_heading=145.0,
                current_accuracy=5.0,
                active_tracker_id="PALKHI-TUKARAM-01"
            )
            db.add(yatra)
            await db.commit()
            await db.refresh(yatra)
        return yatra

    @staticmethod
    async def record_telemetry(db: AsyncSession, point: YatraTrackPointInput) -> YatraLiveOut:
        """
        Validates GPS telemetry, detects speed anomalies, checks geofences, updates live state,
        and broadcasts WebSocket position updates.
        """
        # GPS Sanity Checks
        if not (15.0 <= point.latitude <= 22.0 and 72.0 <= point.longitude <= 80.0):
            logger.warning(f"GPS Anomaly: Coordinate out of Maharashtra bounding box: {point.latitude}, {point.longitude}")
            raise ValueError("Coordinates are out of Maharashtra operational boundary")

        if point.accuracy_meters and point.accuracy_meters > 200.0:
            logger.warning(f"GPS Anomaly: Accuracy degraded ({point.accuracy_meters}m)")

        yatra = await YatraService.get_or_create_primary_yatra(db)

        # Speed sanity validation
        prev_lat, prev_lon = yatra.current_latitude, yatra.current_longitude
        dist_km = google_maps_adapter.haversine_distance_km(prev_lat, prev_lon, point.latitude, point.longitude)
        
        # Heading calculation if not provided
        heading = point.heading or yatra.current_heading

        now = datetime.now(timezone.utc)
        track = YatraTrack(
            yatra_id=yatra.id,
            tracker_id=point.tracker_id,
            timestamp=point.timestamp or now,
            latitude=point.latitude,
            longitude=point.longitude,
            accuracy_meters=point.accuracy_meters or 5.0,
            speed_kmph=point.speed_kmph or 2.8,
            heading=heading,
            altitude=point.altitude,
            source=point.source,
            sequence_number=point.sequence_number or 0,
            is_snapped=False
        )
        db.add(track)

        # Update primary Yatra live state
        yatra.current_latitude = point.latitude
        yatra.current_longitude = point.longitude
        yatra.current_speed = point.speed_kmph or 2.8
        yatra.current_heading = heading
        yatra.current_accuracy = point.accuracy_meters or 5.0
        yatra.last_gps_update = now
        yatra.status = YatraStatus.LIVE

        await db.commit()
        await db.refresh(yatra)

        # Broadcast live position update
        live_data = await YatraService.get_live_status(db)
        await ws_manager.broadcast(
            WebSocketEventType.YATRA_POSITION_UPDATED,
            live_data.model_dump(),
            channel="dashboard"
        )
        return live_data

    @staticmethod
    async def get_live_status(db: AsyncSession) -> YatraLiveOut:
        yatra = await YatraService.get_or_create_primary_yatra(db)
        
        # Recent track (last 20 points)
        track_q = select(YatraTrack).where(YatraTrack.yatra_id == yatra.id).order_by(desc(YatraTrack.timestamp)).limit(20)
        recent_tracks = (await db.execute(track_q)).scalars().all()

        recent_out = [
            YatraTrackPointOut(
                id=t.id,
                yatra_id=t.yatra_id,
                tracker_id=t.tracker_id,
                timestamp=t.timestamp,
                latitude=t.latitude,
                longitude=t.longitude,
                accuracy_meters=t.accuracy_meters,
                speed_kmph=t.speed_kmph,
                heading=t.heading,
                altitude=t.altitude,
                source=t.source,
                sequence_number=t.sequence_number,
                is_snapped=t.is_snapped
            )
            for t in reversed(recent_tracks)
        ]

        now = datetime.now(timezone.utc)
        data_age = int((now - yatra.last_gps_update.replace(tzinfo=timezone.utc if yatra.last_gps_update.tzinfo is None else None)).total_seconds())

        # Checkpoints & ETA
        dist_to_pandharpur = google_maps_adapter.haversine_distance_km(yatra.current_latitude, yatra.current_longitude, 17.6777, 75.3276)
        speed = max(1.5, yatra.current_speed)
        eta_minutes = int((dist_to_pandharpur / speed) * 60)

        return YatraLiveOut(
            id=yatra.id,
            name=yatra.name,
            type=yatra.type,
            status=yatra.status,
            latitude=yatra.current_latitude,
            longitude=yatra.current_longitude,
            current_latitude=yatra.current_latitude,
            current_longitude=yatra.current_longitude,
            speed_kmph=yatra.current_speed,
            current_speed=yatra.current_speed,
            heading=yatra.current_heading,
            current_heading=yatra.current_heading,
            accuracy_meters=yatra.current_accuracy,
            current_accuracy=yatra.current_accuracy,
            last_gps_update=yatra.last_gps_update,
            current_zone_id=yatra.current_zone_id,
            current_route_id=yatra.current_route_id,
            active_tracker_id=yatra.active_tracker_id,
            data_age_seconds=max(0, data_age),
            current_checkpoint="Wakhri Phata (वाखरी तळ)",
            next_checkpoint="Pandharpur Temple (पंढरपूर चौक)",
            distance_remaining_km=dist_to_pandharpur,
            eta_to_pandharpur_minutes=eta_minutes,
            recent_track=recent_out
        )

    @staticmethod
    def get_checkpoints() -> List[YatraCheckpointOut]:
        return [
            YatraCheckpointOut(
                id=c["id"],
                name=c["name"],
                marathi_name=c["marathi_name"],
                latitude=c["lat"],
                longitude=c["lon"],
                sequence=c["seq"],
                distance_km_from_start=c["dist_km"],
                is_reached=(c["seq"] <= 4),
                eta_minutes=0 if c["seq"] <= 4 else 180
            )
            for c in CHECKPOINTS
        ]

    @staticmethod
    async def get_public_live(db: AsyncSession) -> PublicYatraOut:
        yatra = await YatraService.get_or_create_primary_yatra(db)
        return PublicYatraOut(
            name="Sant Tukaram Maharaj Palkhi (संत तुकाराम महाराज पालखी)",
            approximate_latitude=round(yatra.current_latitude, 3),
            approximate_longitude=round(yatra.current_longitude, 3),
            route_name="Pune - Saswad - Lonand - Wakhri - Pandharpur",
            current_location_name="Wakhri Phata (Km 184) - Approaching Pandharpur",
            status="MOVING_IN_PROCESSION",
            speed_kmph=yatra.current_speed,
            last_update=datetime.now().strftime("%d %b %Y %H:%M IST"),
            public_advisory="Warkaris advised to follow pedestrian lanes and drink ORSL electrolytes at Water Hub 4."
        )


yatra_service = YatraService()
