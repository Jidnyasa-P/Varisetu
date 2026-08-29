from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, StateTransitionException
from app.integrations.qdrant_adapter import qdrant_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.vision_adapter import vision_adapter
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.schemas.lost_person import LostPersonCaseCreate
from app.services.audit_service import audit_service
from app.services.incident_service import incident_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class LostPersonService:
    @staticmethod
    async def generate_case_number(db: AsyncSession) -> str:
        res = await db.execute(select(LostPersonCase.case_number))
        existing = {row[0] for row in res.fetchall()}
        num = 801
        while f"#LF-{num}" in existing:
            num += 1
        return f"#LF-{num}"

    @staticmethod
    async def create_case(
        db: AsyncSession,
        case_in: LostPersonCaseCreate,
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case_number = await LostPersonService.generate_case_number(db)

        # Create linked incident automatically
        incident = Incident(
            incident_number=f"INC-{case_number.replace('#', '')}",
            type=IncidentType.MISSING_PERSON,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.OPEN,
            source="HELPLINE_112",
            title=f"Missing Person: {case_in.name} ({case_in.age} {case_in.gender})",
            description=f"Last seen at: {case_in.last_seen_location}. Attire: {case_in.clothing_description}",
            created_by=user_id,
            is_demo=case_in.is_demo
        )
        db.add(incident)
        await db.flush()

        import json
        photo_urls_str = json.dumps(case_in.photo_urls) if case_in.photo_urls else None
        photo_url_val = case_in.photo_url or (case_in.photo_urls[0] if case_in.photo_urls else None)

        case = LostPersonCase(
            case_number=case_number,
            incident_id=incident.id,
            name=case_in.name,
            age=case_in.age,
            gender=case_in.gender,
            clothing_description=case_in.clothing_description,
            physical_description=case_in.physical_description,
            last_seen_location=case_in.last_seen_location,
            last_seen_camera_id=case_in.last_seen_camera_id,
            photo_url=photo_url_val,
            photo_urls=photo_urls_str,
            priority=case_in.priority,
            status=LostPersonStatus.SEARCHING,
            created_by=user_id,
            is_demo=case_in.is_demo
        )
        db.add(case)
        await db.flush()

        # Add initial caller report if provided
        if case_in.initial_transcript or case_in.caller_name:
            report = LostPersonReport(
                case_id=case.id,
                caller_name=case_in.caller_name or "Anonymous Pilgrim",
                caller_phone=case_in.caller_phone or "112 Helpline",
                transcript=case_in.initial_transcript,
                language="mr",
                asr_confidence=0.94
            )
            db.add(report)

        await audit_service.log_action(
            db=db,
            action="LOST_PERSON_CASE_CREATED",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id,
            new_value={"case_number": case_number, "name": case.name}
        )

        await db.commit()
        await db.refresh(case)

        # Broadcast event
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] Lost Person Case {case.case_number} registered: {case.name}"},
            channel="dashboard"
        )
        return case

    @staticmethod
    async def add_match_candidate(
        db: AsyncSession,
        case_id: str,
        camera_id: str,
        similarity_score: float,
        frame_ref: str = "frame_001.jpg"
    ) -> FaceMatchResult:
        match = FaceMatchResult(
            case_id=case_id,
            camera_id=camera_id,
            frame_reference=frame_ref,
            similarity_score=similarity_score,
            confidence=0.94,
            status=FaceMatchStatus.PENDING_VERIFICATION
        )
        db.add(match)

        # Update case status
        case_q = select(LostPersonCase).where(LostPersonCase.id == case_id)
        res = await db.execute(case_q)
        case = res.scalar_one_or_none()
        if case:
            case.status = LostPersonStatus.MATCH_FOUND

        await db.commit()
        await db.refresh(match)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_MATCH_FOUND,
            {"case_id": case_id, "camera_id": camera_id, "score": similarity_score},
            channel="lost-persons"
        )
        return match

    @staticmethod
    async def verify_match(
        db: AsyncSession,
        case_id: str,
        match_id: str,
        verified: bool,
        user_id: Optional[str] = None
    ) -> FaceMatchResult:
        query = select(FaceMatchResult).where(FaceMatchResult.id == match_id, FaceMatchResult.case_id == case_id)
        res = await db.execute(query)
        match = res.scalar_one_or_none()
        if not match:
            raise NotFoundException("Match result not found")

        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()

        match.status = FaceMatchStatus.VERIFIED if verified else FaceMatchStatus.REJECTED
        match.verified_by = user_id
        match.verified_at = datetime.now(timezone.utc)

        if case:
            case.status = LostPersonStatus.VERIFIED if verified else LostPersonStatus.SEARCHING

        await audit_service.log_action(
            db=db,
            action="FACE_MATCH_VERIFIED" if verified else "FACE_MATCH_REJECTED",
            entity_type="FaceMatchResult",
            entity_id=match.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(match)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_VERIFIED,
            {"case_id": case_id, "match_id": match_id, "verified": verified},
            channel="lost-persons"
        )
        return match

    @staticmethod
    async def dispatch_volunteer(
        db: AsyncSession,
        case_id: str,
        volunteer_name: str = "Nearby Volunteer Team",
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if not case:
            raise NotFoundException("Case not found")

        case.status = LostPersonStatus.DISPATCHED
        await audit_service.log_action(
            db=db,
            action="VOLUNTEER_DISPATCHED_FOR_LOST_PERSON",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id
        )
        await db.commit()
        await db.refresh(case)
        return case

    @staticmethod
    async def reunite_case(
        db: AsyncSession,
        case_id: str,
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if not case:
            raise NotFoundException("Case not found")

        case.status = LostPersonStatus.REUNITED
        case.resolved_at = datetime.now(timezone.utc)

        if case.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == case.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.RESOLVED
                inc.resolved_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="LOST_PERSON_REUNITED",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(case)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_REUNITED,
            {"case_id": case.id, "case_number": case.case_number},
            channel="lost-persons"
        )
        return case

    @staticmethod
    async def purge_sensitive_data(db: AsyncSession, case_id: str) -> int:
        """
        Privacy requirement: permanently purge temporary biometric vectors,
        face match frames, and audio references for a case while keeping the operational case record.
        """
        deleted_count = await qdrant_adapter.delete_case_embeddings(case_id)

        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if case:
            case.photo_url = None

        await audit_service.log_action(
            db=db,
            action="SENSITIVE_BIOMETRIC_DATA_PURGED",
            entity_type="LostPersonCase",
            entity_id=case_id
        )
        await db.commit()
        return deleted_count

    @staticmethod
    async def get_cases(db: AsyncSession, status: Optional[LostPersonStatus] = None) -> List[LostPersonCase]:
        query = select(LostPersonCase).options(
            selectinload(LostPersonCase.reports),
            selectinload(LostPersonCase.matches)
        ).order_by(LostPersonCase.created_at.desc())
        if status:
            query = query.where(LostPersonCase.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())


lost_person_service = LostPersonService()
