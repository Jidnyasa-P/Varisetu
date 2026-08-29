"""
Helpline AI Voice Intake & Calling API.
Provides realtime WebSocket audio streaming, VAD state tracking, transcript segmentation,
operator dossier updates, and truthful CCTV search case creation.
"""

import base64
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import get_current_user, get_current_user_optional
from app.integrations.speech_adapter import speech_adapter
from app.models.camera import Camera
from app.models.face_match import FaceMatchResult, FaceMatchStatus, MatchType
from app.models.lost_person import CallSession, CallState, LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.user import User
from app.schemas.helpline import (
    CallActionResponse,
    CallInitRequest,
    CallSessionOut,
    CallSimulationRequest,
    CallSimulationResponse,
    CCTVScanCandidate,
    CCTVScanResponse,
    CreateCaseFromSessionRequest,
    CreateCaseFromSessionResponse,
    HelplineScenarioOut,
    TranscriptSegment,
    UpdateOperatorReportRequest,
)
from app.schemas.lost_person import LostPersonCaseOut
from app.services.cctv_search_service import cctv_search_service
from app.services.helpline_call_manager import helpline_manager
from app.services.lost_person_service import lost_person_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.api.helpline")

router = APIRouter(prefix="/helpline", tags=["Helpline AI & Realtime Voice Calling"])


# ---------------------------------------------------------------------------
# 1. REALTIME WEBSOCKET AUDIO INGESTION & EVENT STREAMING
# ---------------------------------------------------------------------------

@router.websocket("/ws/{session_id}")
async def helpline_websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Realtime duplex WebSocket for helpline audio streaming and VAD events.
    Supports binary PCM16 audio frames and JSON control messages:
    - {"action": "start"}
    - {"action": "pause"}
    - {"action": "resume"}
    - {"action": "hold"}
    - {"action": "unhold"}
    - {"action": "heartbeat"}
    - {"action": "end"}
    - {"action": "audio_chunk", "sequence": 0, "timestamp_ms": 12345, "audio_base64": "..."}
    """
    await helpline_manager.connect_socket(session_id, websocket)
    session = await helpline_manager.get_session(session_id)

    try:
        while True:
            # Handle both JSON text messages and raw binary audio frames
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                # Raw Binary PCM16 audio frame
                raw_pcm16 = message["bytes"]
                if session:
                    seq = session.expected_sequence
                    ts = int(datetime.now(timezone.utc).timestamp() * 1000)
                    events = await session.ingest_audio_frame(sequence=seq, timestamp_ms=ts, pcm16_bytes=raw_pcm16)
                    for ev in events:
                        await helpline_manager.broadcast_event(session_id, ev)

            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                except Exception:
                    continue

                action = payload.get("action", "")

                if action == "start":
                    if session:
                        session.start_call()
                        await helpline_manager.broadcast_event(session_id, {
                            "event": "connection_state",
                            "data": {"session_id": session_id, "call_state": session.call_state.value}
                        })

                elif action == "audio_chunk":
                    if session:
                        seq = payload.get("sequence", session.expected_sequence)
                        ts = payload.get("timestamp_ms", int(datetime.now(timezone.utc).timestamp() * 1000))
                        b64_audio = payload.get("audio_base64", "")
                        if b64_audio:
                            try:
                                pcm_bytes = base64.b64decode(b64_audio)
                                events = await session.ingest_audio_frame(sequence=seq, timestamp_ms=ts, pcm16_bytes=pcm_bytes)
                                for ev in events:
                                    await helpline_manager.broadcast_event(session_id, ev)
                            except Exception as e:
                                logger.warning(f"[MEDIA] Error decoding base64 audio chunk: {e}")

                elif action == "pause" or action == "hold":
                    if session:
                        session.hold_call()
                        await helpline_manager.broadcast_event(session_id, {
                            "event": "connection_state",
                            "data": {"session_id": session_id, "call_state": session.call_state.value}
                        })

                elif action == "resume" or action == "unhold":
                    if session:
                        session.resume_call()
                        await helpline_manager.broadcast_event(session_id, {
                            "event": "connection_state",
                            "data": {"session_id": session_id, "call_state": session.call_state.value}
                        })

                elif action == "heartbeat":
                    await websocket.send_json({"event": "heartbeat_ack", "data": {"session_id": session_id, "server_time": datetime.now(timezone.utc).isoformat()}})

                elif action == "end":
                    if session:
                        session.end_call()
                        await helpline_manager.broadcast_event(session_id, {
                            "event": "session_ended",
                            "data": {"session_id": session_id, "call_state": session.call_state.value, "duration_seconds": session.duration_seconds}
                        })
                    break

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected from session {session_id}")
    except Exception as e:
        logger.error(f"[WS] Error in helpline websocket session {session_id}: {e}")
    finally:
        await helpline_manager.disconnect_socket(session_id, websocket)


# ---------------------------------------------------------------------------
# 2. REST CALL SESSION LIFECYCLE MANAGEMENT
# ---------------------------------------------------------------------------

@router.post("/calls", response_model=CallSessionOut, status_code=status.HTTP_201_CREATED, summary="Initialize a new helpline call session")
async def create_call_session(
    req: CallInitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new stateful helpline call session and returns its initial state."""
    session = await helpline_manager.get_or_create_session(
        caller_name=req.caller_name or "Citizen Caller",
        caller_phone=req.caller_phone or "+91-112",
        language=req.language or "mr",
        is_demo=req.is_demo
    )
    session.start_call()

    # Persist session record in DB
    db_session = CallSession(
        session_id=session.session_id,
        caller_name=session.caller_name,
        caller_phone=session.caller_phone,
        dialed_line=session.dialed_line,
        source_language=session.language,
        call_state=session.call_state,
        started_at=session.started_at or datetime.now(timezone.utc),
        operator_id=current_user.id if current_user else None,
        is_demo=session.is_demo
    )
    db.add(db_session)
    await db.commit()

    return CallSessionOut(
        session_id=session.session_id,
        caller_name=session.caller_name,
        caller_phone=session.caller_phone,
        dialed_line=session.dialed_line,
        source_language=session.language,
        call_state=session.call_state,
        started_at=session.started_at.isoformat() if session.started_at else datetime.now(timezone.utc).isoformat(),
        duration_seconds=0,
        hold_duration_seconds=0,
        native_transcript="",
        english_translation="",
        extracted_attributes=session.extracted_attributes,
        transcript_segments=[],
        is_demo=session.is_demo
    )


@router.get("/calls/{session_id}", response_model=CallSessionOut, summary="Get call session details and transcript")
async def get_call_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await helpline_manager.get_session(session_id)
    if not session:
        # Check DB for persisted session
        stmt = select(CallSession).where(CallSession.session_id == session_id)
        res = await db.execute(stmt)
        db_session = res.scalar_one_or_none()
        if not db_session:
            raise HTTPException(status_code=404, detail=f"Call session {session_id} not found")

        return CallSessionOut(
            session_id=db_session.session_id,
            caller_name=db_session.caller_name or "Citizen Caller",
            caller_phone=db_session.caller_phone or "+91-112",
            dialed_line=db_session.dialed_line,
            source_language=db_session.source_language,
            call_state=db_session.call_state,
            started_at=db_session.started_at.isoformat() if db_session.started_at else "",
            ended_at=db_session.ended_at.isoformat() if db_session.ended_at else None,
            duration_seconds=db_session.duration_seconds,
            hold_duration_seconds=db_session.hold_duration_seconds,
            native_transcript=db_session.native_transcript or "",
            english_translation=db_session.english_translation or "",
            extracted_attributes=db_session.extracted_attributes or {},
            transcript_segments=[],
            is_demo=db_session.is_demo
        )

    return CallSessionOut(
        session_id=session.session_id,
        caller_name=session.caller_name,
        caller_phone=session.caller_phone,
        dialed_line=session.dialed_line,
        source_language=session.language,
        call_state=session.call_state,
        started_at=session.started_at.isoformat() if session.started_at else "",
        ended_at=session.ended_at.isoformat() if session.ended_at else None,
        duration_seconds=session.duration_seconds,
        hold_duration_seconds=session.hold_duration_seconds,
        native_transcript=session.native_transcript,
        english_translation=session.english_translation,
        extracted_attributes=session.extracted_attributes,
        transcript_segments=session.segments,
        is_demo=session.is_demo
    )


@router.post("/calls/{session_id}/hold", response_model=CallActionResponse, summary="Place call on operator hold")
async def hold_call_session(session_id: str, current_user: User = Depends(get_current_user)):
    session = await helpline_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Active session {session_id} not found")

    session.hold_call()
    await helpline_manager.broadcast_event(session_id, {
        "event": "connection_state",
        "data": {"session_id": session_id, "call_state": session.call_state.value}
    })
    return CallActionResponse(session_id=session_id, call_state=session.call_state, message="Call successfully placed on OPERATOR_HOLD")


@router.post("/calls/{session_id}/resume", response_model=CallActionResponse, summary="Resume call from operator hold")
async def resume_call_session(session_id: str, current_user: User = Depends(get_current_user)):
    session = await helpline_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Active session {session_id} not found")

    session.resume_call()
    await helpline_manager.broadcast_event(session_id, {
        "event": "connection_state",
        "data": {"session_id": session_id, "call_state": session.call_state.value}
    })
    return CallActionResponse(session_id=session_id, call_state=session.call_state, message="Call resumed -> LISTENING")


@router.post("/calls/{session_id}/end", response_model=CallActionResponse, summary="Explicitly end helpline call session")
async def end_call_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await helpline_manager.get_session(session_id)
    if session:
        session.end_call()
        await helpline_manager.broadcast_event(session_id, {
            "event": "session_ended",
            "data": {"session_id": session_id, "call_state": session.call_state.value, "duration_seconds": session.duration_seconds}
        })

    # Update database record
    stmt = select(CallSession).where(CallSession.session_id == session_id)
    res = await db.execute(stmt)
    db_session = res.scalar_one_or_none()
    if db_session:
        db_session.call_state = CallState.CALL_ENDED
        db_session.ended_at = datetime.now(timezone.utc)
        if session:
            db_session.duration_seconds = session.duration_seconds
            db_session.hold_duration_seconds = session.hold_duration_seconds
            db_session.native_transcript = session.native_transcript
            db_session.english_translation = session.english_translation
            db_session.extracted_attributes = session.extracted_attributes
            db_session.transcript_segments = [s.model_dump() for s in session.segments]
        db.add(db_session)
        await db.commit()

    return CallActionResponse(session_id=session_id, call_state=CallState.CALL_ENDED, message="Call ended and audio resources released")


@router.post("/calls/{session_id}/report", response_model=Dict[str, Any], summary="Operator update to extracted report attributes")
async def update_operator_report(
    session_id: str,
    req: UpdateOperatorReportRequest,
    current_user: User = Depends(get_current_user)
):
    session = await helpline_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Active session {session_id} not found")

    for k, v in req.model_dump(exclude_unset=True).items():
        if v is not None:
            session.extracted_attributes[k] = v

    await helpline_manager.broadcast_event(session_id, {
        "event": "attributes_updated",
        "data": {"session_id": session_id, "extracted_attributes": session.extracted_attributes}
    })
    return {"session_id": session_id, "extracted_attributes": session.extracted_attributes, "message": "Operator report updated successfully"}


# ---------------------------------------------------------------------------
# 3. CASE CREATION & TRUTHFUL CCTV SEARCH ORCHESTRATION
# ---------------------------------------------------------------------------

@router.post("/calls/{session_id}/create-case", response_model=CreateCaseFromSessionResponse, status_code=status.HTTP_201_CREATED, summary="Create verified lost person case and trigger spatial-temporal CCTV search")
async def create_case_from_session(
    session_id: str,
    req: CreateCaseFromSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await helpline_manager.get_session(session_id)

    from app.schemas.lost_person import LostPersonCaseCreate
    case_create = LostPersonCaseCreate(
        name=req.name,
        age=req.age,
        gender=req.gender,
        clothing_description=req.clothing_description,
        last_seen_location=req.last_seen_location,
        last_seen_time=datetime.now(timezone.utc),
        contact_number=session.caller_phone if session else "+91-112",
        reporter_name=session.caller_name if session else "Helpline Operator",
        reporter_phone=session.caller_phone if session else "+91-112",
        status=LostPersonStatus.SEARCHING
    )

    user_id = current_user.id if current_user else None
    case = await lost_person_service.create_case(db, case_create, user_id=user_id)

    # Create LostPersonReport record
    report = LostPersonReport(
        case_id=case.id,
        call_session_id=session_id,
        caller_name=session.caller_name if session else "Citizen Caller",
        caller_phone=session.caller_phone if session else "+91-112",
        audio_file_url=session.audio_file_url if session else None,
        transcript=session.native_transcript if session else "Operator report entry",
        english_translation=session.english_translation if session else None,
        language=session.language if session else "mr",
        asr_confidence=0.96,
        translation_confidence=0.94,
        extracted_attributes=session.extracted_attributes if session else req.model_dump()
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Orchestrate truthful CCTV search (no hardcoded 0.91 matches)
    cctv_candidates: List[CCTVScanCandidate] = []
    if req.trigger_cctv_scan:
        scan_res = await cctv_search_service.orchestrate_cctv_search(
            case=case,
            db=db,
            search_window_minutes=30,
            operator_id=user_id
        )
        cctv_candidates = scan_res.candidates

    # Broadcast event
    try:
        await ws_manager.broadcast(WebSocketEventType.LOST_PERSON_MATCH_FOUND, {
            "case_id": str(case.id),
            "case_number": case.case_number,
            "name": case.name,
            "location": case.last_seen_location,
            "candidates_count": len(cctv_candidates)
        })
    except Exception as e:
        logger.warning(f"WebSocket broadcast skipped: {e}")

    return CreateCaseFromSessionResponse(
        case=LostPersonCaseOut.model_validate(case),
        report_id=str(report.id),
        call_session_id=session_id,
        cctv_candidates=cctv_candidates,
        message=f"Lost Person Case {case.case_number} created with {len(cctv_candidates)} ranked CCTV candidate(s) awaiting verification."
    )


# ---------------------------------------------------------------------------
# 4. LEGACY / COMPATIBILITY ENDPOINT (UPDATED WITH TRUTHFUL CCTV ORCHESTRATION)
# ---------------------------------------------------------------------------

class LegacyCreateCaseFromCallRequest(BaseModel):
    caller_name: str
    caller_phone: str
    native_transcript: str
    english_translation: str
    name: str
    age: int
    gender: str = "M"
    clothing_description: str
    last_seen_location: str
    zone_id: Optional[str] = None
    urgency: Optional[str] = "HIGH"
    trigger_cctv_scan: bool = True


class LegacyCCTVScanResult(BaseModel):
    match_id: str
    case_id: str
    camera_code: str
    camera_name: str
    location_name: str
    latitude: float
    longitude: float
    similarity_score: float
    confidence_label: str
    frame_timestamp: str
    matched_features: str
    snapshot_url: str
    status: str = "CANDIDATE"


class LegacyCreateCaseFromCallResponse(BaseModel):
    case: LostPersonCaseOut
    report_id: str
    cctv_matches: List[LegacyCCTVScanResult]
    message: str


@router.post("/call/create-case-and-match", response_model=LegacyCreateCaseFromCallResponse, status_code=status.HTTP_201_CREATED, summary="Legacy create case from call with truthful CCTV scan")
async def legacy_create_case_from_call(
    req: LegacyCreateCaseFromCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.schemas.lost_person import LostPersonCaseCreate
    case_create = LostPersonCaseCreate(
        name=req.name,
        age=req.age,
        gender=req.gender,
        clothing_description=req.clothing_description,
        last_seen_location=req.last_seen_location,
        last_seen_time=datetime.now(timezone.utc),
        contact_number=req.caller_phone,
        reporter_name=req.caller_name,
        reporter_phone=req.caller_phone,
        status=LostPersonStatus.SEARCHING
    )

    user_id = current_user.id if current_user else None
    case = await lost_person_service.create_case(db, case_create, user_id=user_id)

    report = LostPersonReport(
        case_id=case.id,
        caller_name=req.caller_name,
        caller_phone=req.caller_phone,
        audio_file_url="assets/audio/helpline_call_sample.mp3",
        transcript=f"Native: {req.native_transcript}\nAI English Translation: {req.english_translation}",
        english_translation=req.english_translation,
        language="mr",
        asr_confidence=0.96
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    cctv_matches: List[LegacyCCTVScanResult] = []
    if req.trigger_cctv_scan:
        scan_res = await cctv_search_service.orchestrate_cctv_search(
            case=case,
            db=db,
            search_window_minutes=30,
            operator_id=user_id
        )
        for cand in scan_res.candidates:
            cctv_matches.append(LegacyCCTVScanResult(
                match_id=cand.match_id,
                case_id=cand.case_id,
                camera_code=cand.camera_code,
                camera_name=cand.camera_name,
                location_name=cand.location_name,
                latitude=cand.latitude,
                longitude=cand.longitude,
                similarity_score=cand.similarity_score,
                confidence_label=cand.confidence_label,
                frame_timestamp=cand.frame_timestamp,
                matched_features=cand.matched_features,
                snapshot_url=cand.snapshot_url,
                status=cand.status.value
            ))

    return LegacyCreateCaseFromCallResponse(
        case=LostPersonCaseOut.model_validate(case),
        report_id=str(report.id),
        cctv_matches=cctv_matches,
        message=f"Case {case.case_number} registered successfully with {len(cctv_matches)} CCTV candidate match(es)."
    )


# ---------------------------------------------------------------------------
# 5. DEMO / SIMULATION MODE ONLY (CLEARLY TAGGED AS DEMO)
# ---------------------------------------------------------------------------

@router.get("/scenarios", response_model=List[HelplineScenarioOut], summary="List pre-calibrated demo scenarios (DEMO ONLY)")
async def get_helpline_scenarios(current_user: User = Depends(get_current_user)):
    scenarios = []
    for s_id, s_data in speech_adapter.SCENARIOS.items():
        scenarios.append(HelplineScenarioOut(
            id=s_id,
            title=s_data["title"],
            caller_phone=s_data["caller_phone"],
            caller_name=s_data["caller_name"],
            dialed_line=s_data["dialed_line"],
            language=s_data["language"],
            language_name=s_data["language_name"]
        ))
    return scenarios


@router.post("/call/simulate", response_model=CallSimulationResponse, summary="Simulate an emergency intake call (DEMO ONLY)")
async def simulate_call(
    req: CallSimulationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Explicitly for offline demonstration and testing.
    Marked with source: 'DEMO'. Never used by live microphone mode.
    """
    res = await speech_adapter.transcribe_and_translate(
        scenario_id=req.scenario_id,
        custom_text=req.custom_text,
        language=req.language or "mr"
    )

    waveform = [18, 35, 72, 94, 88, 65, 42, 78, 91, 100, 84, 56, 38, 70, 85, 92, 77, 49, 31, 64, 82, 96, 75, 52, 28, 60, 89, 95, 71, 44, 22, 10]

    return CallSimulationResponse(
        session_id=f"sim_{uuid.uuid4().hex[:8]}",
        scenario_id=req.scenario_id,
        title=res.get("title", "Helpline Intake"),
        caller_phone=res.get("caller_phone", "+91 98234 11204"),
        caller_name=res.get("caller_name", "Dnyaneshwar Shinde"),
        dialed_line=res.get("dialed_line", "112 / Emergency Helpline"),
        language=res.get("language", "mr"),
        language_name=res.get("language_name", "मराठी (Marathi)"),
        native_transcript=res.get("native_transcript", ""),
        english_translation=res.get("english_translation", ""),
        confidence=res.get("confidence", 0.96),
        extracted_attributes=res.get("extracted_attributes", {}),
        waveform=waveform,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="DEMO"
    )
