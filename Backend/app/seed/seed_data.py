import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.rbac import UserRole
from app.core.security import get_password_hash
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.medical import MedicalAlert, MedicalAlertStatus, MedicalAlertType
from app.models.notification import Notification, NotificationType
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability, ResourceType
from app.models.route import Route, RouteStatus
from app.models.user import User
from app.models.zone import RiskLevel, Zone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("varisetu.seed")


async def seed_database():
    async with AsyncSessionLocal() as db:
        # Check if users already exist
        existing_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if existing_user:
            logger.info("Database already seeded. Skipping...")
            return

        logger.info("Seeding users...")
        users = [
            User(
                name="Command Center Controller",
                email="control.room@mahapolice.gov.in",
                phone="+91-9822001122",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.ADMIN,
                department="Maharashtra Police IT Cell",
                is_active=True
            ),
            User(
                name="Inspector R. K. Patil",
                email="police.officer@mahapolice.gov.in",
                phone="+91-9822003344",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.POLICE,
                department="Pandharpur Traffic Division",
                is_active=True
            ),
            User(
                name="Dr. Shubhada Deshmukh",
                email="medical.team@varisetu.org",
                phone="+91-9822005566",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.MEDICAL,
                department="Emergency Health Services",
                is_active=True
            )
        ]
        db.add_all(users)
        await db.flush()

        logger.info("Seeding zones...")
        zones = [
            Zone(name="Pandharpur Chowk", description="Main temple entry plaza bottleneck", latitude=17.6777, longitude=75.3276, capacity=60000, risk_level=RiskLevel.CRITICAL),
            Zone(name="Wakhri Phata", description="Major highway diversion and camp junction", latitude=17.7280, longitude=75.2950, capacity=45000, risk_level=RiskLevel.HIGH),
            Zone(name="Vakhri Naka", description="Bridge approach choke point", latitude=17.7500, longitude=75.2700, capacity=35000, risk_level=RiskLevel.HIGH),
            Zone(name="Saswad Highway Stop", description="Intermediate resting shelter", latitude=18.3440, longitude=74.0305, capacity=25000, risk_level=RiskLevel.MODERATE),
            Zone(name="Tarapur Phata", description="Bypass junction for supply convoys", latitude=17.8000, longitude=75.1500, capacity=20000, risk_level=RiskLevel.LOW),
            Zone(name="Alandi Corridor", description="Procession starting ghats", latitude=18.6772, longitude=73.8967, capacity=50000, risk_level=RiskLevel.LOW),
        ]
        db.add_all(zones)
        await db.flush()
        zone_map = {z.name: z.id for z in zones}

        logger.info("Seeding cameras...")
        cameras = [
            Camera(camera_code="CAM-01", name="Alandi Ghat Section Cam 01", zone_id=zone_map["Alandi Corridor"], latitude=18.6772, longitude=73.8967, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-04", name="Pandharpur Temple Chowk Cam 04", zone_id=zone_map["Pandharpur Chowk"], latitude=17.6777, longitude=75.3276, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-08", name="Saswad Highway Checkpoint Cam 08", zone_id=zone_map["Saswad Highway Stop"], latitude=18.3440, longitude=74.0305, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-12", name="Wakhri Phata Junction Cam 12", zone_id=zone_map["Wakhri Phata"], latitude=17.7280, longitude=75.2950, status=CameraStatus.ONLINE),
        ]
        db.add_all(cameras)
        await db.flush()
        cam_map = {c.camera_code: c.id for c in cameras}

        logger.info("Seeding crowd observations...")
        observations = [
            CrowdObservation(camera_id=cam_map["CAM-04"], zone_id=zone_map["Pandharpur Chowk"], density_percentage=94.0, people_count=2850, movement_direction="SOUTH", trend=CrowdTrend.RISING, risk_level=RiskLevel.CRITICAL, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-12"], zone_id=zone_map["Wakhri Phata"], density_percentage=88.0, people_count=1420, movement_direction="EAST", trend=CrowdTrend.RISING, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-08"], zone_id=zone_map["Saswad Highway Stop"], density_percentage=62.0, people_count=890, movement_direction="SOUTH", trend=CrowdTrend.EASING, risk_level=RiskLevel.MODERATE, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-01"], zone_id=zone_map["Alandi Corridor"], density_percentage=35.0, people_count=410, movement_direction="SOUTH", trend=CrowdTrend.STABLE, risk_level=RiskLevel.LOW, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Vakhri Naka"], density_percentage=74.0, people_count=1100, trend=CrowdTrend.STABLE, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Tarapur Phata"], density_percentage=28.0, people_count=320, trend=CrowdTrend.FALLING, risk_level=RiskLevel.LOW, source="DEMO"),
        ]
        db.add_all(observations)

        logger.info("Seeding incidents & events...")
        incidents = [
            Incident(
                incident_number="INC-2026-0825-001",
                type=IncidentType.CROWD,
                severity=IncidentSeverity.HIGH,
                status=IncidentStatus.OPEN,
                source="CCTV_AI",
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                title="Crowd density surge detected at Wakhri Phata (88%)",
                description="Pedestrian flow bottleneck causing slow movement. Recommendation: Divert queue to North Ring Road.",
                is_demo=True
            ),
            Incident(
                incident_number="INC-2026-0825-002",
                type=IncidentType.ROAD_BLOCK,
                severity=IncidentSeverity.MEDIUM,
                status=IncidentStatus.IN_PROGRESS,
                source="OPERATOR",
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                title="Solapur Highway Diversion Gate 2 opened",
                description="Traffic diverted to secondary bypass for VIP procession escort.",
                is_demo=True
            )
        ]
        db.add_all(incidents)
        await db.flush()

        events = [
            IncidentEvent(incident_id=incidents[0].id, event_type="CROWD_PEAK", message="CAM-12 Wakhri Phata: Density peak detected (88%)"),
            IncidentEvent(incident_id=incidents[1].id, event_type="ROUTE_DIVERTED", message="Solapur Highway Diversion Gate 2 opened for traffic relief")
        ]
        db.add_all(events)

        logger.info("Seeding lost person cases...")
        lost_cases = [
            LostPersonCase(
                case_number="#LF-802",
                name="Maruti Kisan Shinde",
                age=68,
                gender="M",
                clothing_description="पांढरा कुर्ता, धोती, पांढरी टोपी (White Kurta-Dhoti, Gandhi topi, Tulsi mala)",
                last_seen_location="Pandharpur Temple Chowk",
                last_seen_camera_id=cam_map["CAM-04"],
                priority="HIGH",
                status=LostPersonStatus.MATCH_FOUND,
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-805",
                name="Anandita Ramesh Kulkarni",
                age=9,
                gender="F",
                clothing_description="पिवळा परकर पोलका (Yellow traditional dress, red ribbons)",
                last_seen_location="Wakhri Phata Rest Camp",
                last_seen_camera_id=cam_map["CAM-12"],
                priority="CRITICAL",
                status=LostPersonStatus.SEARCHING,
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-799",
                name="Dnyaneshwar Mahadev Jadhav",
                age=72,
                gender="M",
                clothing_description="पांढरा पोशाख, लाल पटका (White attire with red turban)",
                last_seen_location="Saswad Highway Checkpoint",
                last_seen_camera_id=cam_map["CAM-08"],
                priority="NORMAL",
                status=LostPersonStatus.REUNITED,
                resolved_at=datetime.now(timezone.utc),
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-808",
                name="Sunita Vitthal Patil",
                age=54,
                gender="F",
                clothing_description="हिरवी नऊवारी साडी (Green Nauvari saree)",
                last_seen_location="Alandi Ghat Section",
                last_seen_camera_id=cam_map["CAM-01"],
                priority="HIGH",
                status=LostPersonStatus.SEARCHING,
                is_demo=True
            )
        ]
        db.add_all(lost_cases)
        await db.flush()

        # Add Marathi reports & Face matches
        reports = [
            LostPersonReport(
                case_id=lost_cases[0].id,
                caller_name="Namdeo Shinde (Grandson)",
                caller_phone="+91-9822014455",
                transcript="हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत.",
                language="mr",
                asr_confidence=0.94
            ),
            LostPersonReport(
                case_id=lost_cases[1].id,
                caller_name="Ramesh Kulkarni (Father)",
                caller_phone="+91-9822019988",
                transcript="माझी मुलगी आनंदिता वय ९ वर्षे वाखरी विश्राम शिबिराजवळ सुटली आहे. तिने पिवळा परकर पोलका घातला आहे.",
                language="mr",
                asr_confidence=0.96
            ),
            LostPersonReport(
                case_id=lost_cases[3].id,
                caller_name="Vitthal Patil (Husband)",
                caller_phone="+91-9822013322",
                transcript="माझी पत्नी सुनिता पाटील आळंदी घाट जवळ दिंडीतून पुढे निघून गेली आहे, हिरवी नऊवारी साडी आहे.",
                language="mr",
                asr_confidence=0.91
            )
        ]
        db.add_all(reports)

        matches = [
            FaceMatchResult(
                case_id=lost_cases[0].id,
                camera_id=cam_map["CAM-04"],
                frame_reference="frame_4812.jpg",
                similarity_score=0.89,
                confidence=0.94,
                status=FaceMatchStatus.PENDING_VERIFICATION
            )
        ]
        db.add_all(matches)

        logger.info("Seeding medical alerts...")
        medical_alerts = [
            MedicalAlert(
                alert_code="MED-101",
                type=MedicalAlertType.FALL,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                description="FALL DETECTED / FAINTING PILGRIM (Wakhri Phata Km 184) - Dispatching First Responder",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Team Bravo (V. R. Kadam)",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-102",
                type=MedicalAlertType.HEAT_EXHAUSTION,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Pandharpur Chowk"],
                camera_id=cam_map["CAM-04"],
                latitude=17.6777,
                longitude=75.3276,
                description="CROWD HEAT EXHAUSTION RISK (SECTOR 5) - Ambient Temp 34°C, High Humidity",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Medical Van #MV-02",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-098",
                type=MedicalAlertType.DEHYDRATION,
                severity=IncidentSeverity.MEDIUM,
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                description="DEHYDRATION ASSIST & REHYDRATION (RESOLVED) - Pilgrim treated with ORSL salt packets",
                status=MedicalAlertStatus.RESOLVED,
                assigned_volunteer_name="Red Cross Volunteer Post #3",
                resolved_at=datetime.now(timezone.utc),
                is_demo=True
            )
        ]
        db.add_all(medical_alerts)

        logger.info("Seeding resources & vehicles...")
        resources = [
            Resource(resource_code="WT-09", name="10,000L Water Tanker #09", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Station Standby"),
            Resource(resource_code="WT-04", name="10,000L Water Tanker #04", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="DEPLOYED", availability=ResourceAvailability.ASSIGNED, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Temple Gate North"),
            Resource(resource_code="WT-12", name="10,000L Water Tanker #12", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=18.3440, longitude=74.0305, zone_id=zone_map["Saswad Highway Stop"], location_description="Saswad Rest Post"),
            Resource(resource_code="MV-02", name="Mobile Medical Van #02 (Ambulance)", resource_type=ResourceType.MEDICAL_VAN, capacity=4, status_tag="ACTIVE", availability=ResourceAvailability.ASSIGNED, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Sector 4 Base"),
            Resource(resource_code="MV-05", name="Emergency Ambulance #05", resource_type=ResourceType.AMBULANCE, capacity=2, status_tag="STANDBY", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Pandharpur Civil Hospital"),
            Resource(resource_code="PS-14", name="Police Patrol Squad #14", resource_type=ResourceType.POLICE_SQUAD, capacity=8, status_tag="ACTIVE", availability=ResourceAvailability.ON_SCENE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Bottleneck Patrol"),
            Resource(resource_code="VT-08", name="Dindi Volunteer Stewards (Squad 8)", resource_type=ResourceType.VOLUNTEER_TEAM, capacity=25, status_tag="ACTIVE", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Chhatrapati Shivaji Chowk"),
        ]
        db.add_all(resources)

        logger.info("Seeding routes...")
        routes = [
            Route(name="NH-9 Solapur Highway Junction", description="Primary vehicle thoroughfare", status=RouteStatus.DIVERTED, priority="PRIMARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.6777, longitude_end=75.3276),
            Route(name="Pune-Saswad Pilgrimage Road", description="Dedicated pedestrian corridor for Palkhi procession", status=RouteStatus.PILGRIMS_ONLY, priority="PRIMARY", latitude_start=18.6772, longitude_start=73.8967, latitude_end=18.3440, longitude_end=74.0305),
            Route(name="Wakhri Phata Inner Access Road", description="Narrow passage near temporary tents", status=RouteStatus.CLOSED, priority="SECONDARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.7500, longitude_end=75.2700),
            Route(name="Pandharpur Temple Ring Road", description="Reserved exclusively for ambulances and police emergency vehicles", status=RouteStatus.EMERGENCY_ACCESS, priority="PRIMARY", latitude_start=17.6777, longitude_start=75.3276, latitude_end=17.6850, longitude_end=75.3400),
        ]
        db.add_all(routes)

        logger.info("Seeding notifications...")
        notifications = [
            Notification(type=NotificationType.CROWD, title="Crowd Congestion Warning", message="Density at Wakhri Phata crossed 85%. Automated queue diversion suggested.", priority="HIGH"),
            Notification(type=NotificationType.MEDICAL, title="Medical Emergency Dispatched", message="Ambulance MV-02 dispatched to Sector 4 for fainting pilgrim.", priority="HIGH"),
            Notification(type=NotificationType.LOST_PERSON, title="AI Face Match Candidate", message="Candidate match with 89% similarity found on CAM-04 for #LF-802.", priority="NORMAL"),
        ]
        db.add_all(notifications)

        logger.info("Seeding Yatra / Palkhi live state...")
        from app.models.yatra import Yatra, YatraStatus, YatraTrack
        from app.models.announcement import PublicAnnouncement, AnnouncementStatus

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
        await db.flush()

        track_pts = [
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=18.0400, longitude=74.1900, speed_kmph=3.0, heading=140.0, source="GPS_DEVICE", sequence_number=1),
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=17.8900, longitude=75.0200, speed_kmph=2.9, heading=142.0, source="GPS_DEVICE", sequence_number=2),
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=17.7280, longitude=75.2950, speed_kmph=2.8, heading=145.0, source="GPS_DEVICE", sequence_number=3),
        ]
        db.add_all(track_pts)

        logger.info("Seeding Public Announcements...")
        announcements = [
            PublicAnnouncement(
                message_mr="सर्व वारकऱ्यांना नम्र विनंती: वाखरी फाटा येथे गर्दी जास्त असल्याने कृपया पर्यायी पायी मार्गाचा वापर करावा.",
                message_en="All pilgrims are requested to use the designated pedestrian bypass route due to high crowd density at Wakhri Phata.",
                priority="HIGH",
                status=AnnouncementStatus.BROADCAST,
                broadcast_at=datetime.now(timezone.utc)
            ),
            PublicAnnouncement(
                message_mr="विनामूल्य ओआरएसएल (ORSL) आणि पाणी वाटप केंद्र क्र. ४ वर उपलब्ध आहे.",
                message_en="Free ORSL rehydration sachets and drinking water available at Hub No. 4.",
                priority="NORMAL",
                status=AnnouncementStatus.APPROVED
            )
        ]
        db.add_all(announcements)

        await db.commit()
        logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())

