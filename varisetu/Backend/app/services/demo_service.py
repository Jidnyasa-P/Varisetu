import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.database import AsyncSessionLocal
from app.models.crowd import CrowdTrend
from app.models.incident import IncidentSeverity, IncidentType
from app.models.medical import MedicalAlertType
from app.schemas.crowd import CrowdObservationCreate
from app.schemas.incident import IncidentCreate
from app.schemas.lost_person import LostPersonCaseCreate
from app.schemas.medical import MedicalAlertCreate
from app.services.crowd_service import crowd_service
from app.services.incident_service import incident_service
from app.services.lost_person_service import lost_person_service
from app.services.medical_service import medical_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.demo")


class DemoService:
    def __init__(self):
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self.current_step: int = 0
        self.total_steps: int = 12
        self.started_at: Optional[datetime] = None

    async def start(self) -> Dict[str, str]:
        if self.is_running:
            return {"status": "already_running", "message": "Demo simulation is already active."}

        self.is_running = True
        self.current_step = 0
        self.started_at = datetime.now(timezone.utc)
        self._task = asyncio.create_task(self._run_scenario())
        logger.info("Demo simulation engine started.")
        return {"status": "started", "message": "Demo pilgrimage operational simulation started."}

    async def stop(self) -> Dict[str, str]:
        if not self.is_running:
            return {"status": "not_running", "message": "Demo simulation is not running."}

        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Demo simulation engine stopped.")
        return {"status": "stopped", "message": "Demo simulation stopped."}

    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "started_at": self.started_at.isoformat() if self.started_at else None
        }

    async def _run_scenario(self):
        """Execute end-to-end Wari pilgrimage emergency simulation steps."""
        try:
            # STEP 1: Crowd density increases at Wakhri Phata
            self.current_step = 1
            async with AsyncSessionLocal() as db:
                from app.models.zone import Zone
                from sqlalchemy import select
                wakhri = (await db.execute(select(Zone).where(Zone.name.ilike("%Wakhri%")))).scalar_one_or_none()
                if wakhri:
                    await crowd_service.record_observation(
                        db,
                        CrowdObservationCreate(
                            zone_id=wakhri.id,
                            density_percentage=88.0,
                            people_count=1420,
                            trend=CrowdTrend.RISING,
                            source="DEMO"
                        )
                    )
            await ws_manager.broadcast(
                WebSocketEventType.TICKER_EVENT,
                {"text": f"[{datetime.now().strftime('%H:%M:%S')}] [DEMO] CAM-12 Wakhri Phata: Density surge detected (88%)"},
                channel="dashboard"
            )
            await asyncio.sleep(4)

            # STEP 2: Crowd Incident Created
            self.current_step = 2
            async with AsyncSessionLocal() as db:
                inc = await incident_service.create_incident(
                    db,
                    IncidentCreate(
                        title="Crowd Congestion Surge at Wakhri Phata Junction",
                        type=IncidentType.CROWD,
                        severity=IncidentSeverity.HIGH,
                        description="Density crossed 85% safety threshold at pedestrian bottleneck.",
                        source="CCTV_AI",
                        is_demo=True
                    )
                )
                inc_id = inc.id
            await asyncio.sleep(4)

            # STEP 3: Medical Fall Alert
            self.current_step = 3
            async with AsyncSessionLocal() as db:
                med_alert = await medical_service.create_alert(
                    db,
                    MedicalAlertCreate(
                        type=MedicalAlertType.FALL,
                        severity=IncidentSeverity.HIGH,
                        latitude=17.7280,
                        longitude=75.2950,
                        description="Fall detected / Fainting pilgrim near Wakhri Phata Km 184.",
                        is_demo=True
                    )
                )
                med_id = med_alert.id
            await asyncio.sleep(4)

            # STEP 4: Medical Alert Acknowledged
            self.current_step = 4
            async with AsyncSessionLocal() as db:
                await medical_service.acknowledge_alert(
                    db,
                    med_id,
                    volunteer_name="Team Bravo (V. R. Kadam)"
                )
            await asyncio.sleep(4)

            # STEP 5: Lost Person Case Registered
            self.current_step = 5
            async with AsyncSessionLocal() as db:
                lost_case = await lost_person_service.create_case(
                    db,
                    LostPersonCaseCreate(
                        name="Maruti Kisan Shinde",
                        age=68,
                        gender="M",
                        clothing_description="पांढरा कुर्ता, धोती, पांढरी टोपी (White Kurta-Dhoti, Gandhi topi, carrying Tulsi mala)",
                        last_seen_location="Wakhri Phata Junction",
                        caller_name="Namdeo Shinde (Grandson)",
                        caller_phone="+91-9822014455",
                        initial_transcript=(
                            "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                            "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे."
                        ),
                        is_demo=True
                    )
                )
                case_id = lost_case.id
            await asyncio.sleep(4)

            # STEP 6: AI Face Match Candidate Generated
            self.current_step = 6
            async with AsyncSessionLocal() as db:
                match = await lost_person_service.add_match_candidate(
                    db,
                    case_id=case_id,
                    camera_id="CAM-04",
                    similarity_score=0.89,
                    frame_ref="frame_4812.jpg"
                )
                match_id = match.id
            await ws_manager.broadcast(
                WebSocketEventType.TICKER_EVENT,
                {"text": f"[{datetime.now().strftime('%H:%M:%S')}] [DEMO] Lost Person Case #{case_id[:8]}: AI Candidate match 89% on CAM-04"},
                channel="dashboard"
            )
            await asyncio.sleep(4)

            # STEP 7: Officer Verifies Face Match
            self.current_step = 7
            async with AsyncSessionLocal() as db:
                await lost_person_service.verify_match(
                    db,
                    case_id=case_id,
                    match_id=match_id,
                    verified=True
                )
            await asyncio.sleep(4)

            # STEP 8: Volunteer Dispatched for Lost Person
            self.current_step = 8
            async with AsyncSessionLocal() as db:
                await lost_person_service.dispatch_volunteer(
                    db,
                    case_id=case_id,
                    volunteer_name="Volunteer Squad Pandharpur North"
                )
            await asyncio.sleep(4)

            # STEP 9: Pilgrim Reunited
            self.current_step = 9
            async with AsyncSessionLocal() as db:
                await lost_person_service.reunite_case(db, case_id=case_id)
            await asyncio.sleep(4)

            # STEP 10: Medical Alert Resolved
            self.current_step = 10
            async with AsyncSessionLocal() as db:
                await medical_service.resolve_alert(
                    db,
                    alert_id=med_id,
                    resolution_notes="Pilgrim rehydrated with ORSL and reunited with Dindi group."
                )
            await asyncio.sleep(4)

            # STEP 11: Incident Resolved
            self.current_step = 11
            async with AsyncSessionLocal() as db:
                await incident_service.resolve_incident(
                    db,
                    incident_id=inc_id,
                    resolution_notes="Pedestrian traffic cleared; queue diversion completed."
                )
            await asyncio.sleep(3)

            # STEP 12: Complete
            self.current_step = 12
            self.is_running = False
            logger.info("Demo pilgrimage operational simulation completed successfully.")

        except asyncio.CancelledError:
            self.is_running = False
            logger.info("Demo simulation cancelled.")
        except Exception as e:
            self.is_running = False
            logger.error(f"Demo simulation error: {e}", exc_info=True)


demo_service = DemoService()
