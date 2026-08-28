from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.integrations.notification_adapter import notification_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.storage_adapter import storage_adapter
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.user import User
from app.schemas.lost_person import (
    FaceMatchOut,
    FaceMatchVerifyRequest,
    LostPersonCaseCreate,
    LostPersonCaseOut,
    LostPersonReportOut,
    PurgeSensitiveDataResponse
)
from app.services.lost_person_service import lost_person_service

router = APIRouter(prefix="/lost-persons", tags=["Lost & Found"], dependencies=[Depends(get_current_user)])


import json

def _format_case_out(c: LostPersonCase) -> LostPersonCaseOut:
    out = LostPersonCaseOut.model_validate(c)
    if c.photo_urls:
        if isinstance(c.photo_urls, str):
            try:
                out.photo_urls = json.loads(c.photo_urls)
            except Exception:
                out.photo_urls = [c.photo_urls]
        elif isinstance(c.photo_urls, list):
            out.photo_urls = c.photo_urls
    elif c.photo_url:
        out.photo_urls = [c.photo_url]
    return out


@router.get("", response_model=List[LostPersonCaseOut], summary="List lost person cases")
async def list_lost_person_cases(
    status: Optional[LostPersonStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    cases = await lost_person_service.get_cases(db, status=status)
    return [_format_case_out(c) for c in cases]


@router.post("", response_model=LostPersonCaseOut, status_code=status.HTTP_201_CREATED, summary="Register missing person case")
async def create_case(
    case_in: LostPersonCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.create_case(db, case_in, user_id=user_id)
    return _format_case_out(case)


@router.get("/{id}", response_model=LostPersonCaseOut, summary="Get lost person case details")
async def get_case(id: str, db: AsyncSession = Depends(get_db)):
    query = select(LostPersonCase).where(
        (LostPersonCase.id == id) | (LostPersonCase.case_number == id)
    ).options(
        selectinload(LostPersonCase.reports),
        selectinload(LostPersonCase.matches)
    )
    case = (await db.execute(query)).scalar_one_or_none()
    if not case:
        raise NotFoundException("Lost person case not found")
    return _format_case_out(case)


@router.post("/{id}/audio", response_model=LostPersonReportOut, summary="Upload & transcribe helpline call recording")
async def upload_audio_report(
    id: str,
    file: UploadFile = File(...),
    caller_name: Optional[str] = Form(None),
    caller_phone: Optional[str] = Form(None),
    language: str = Form("mr"),
    db: AsyncSession = Depends(get_db)
):
    case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == id))).scalar_one_or_none()
    if not case:
        raise NotFoundException("Case not found")

    content = await file.read()
    filename = f"case_{case.case_number}_{file.filename}"
    file_url = await storage_adapter.save_file(filename, content)

    # Perform Speech-to-Text via adapter
    asr_res = await speech_adapter.transcribe(content, language=language)

    report = LostPersonReport(
        case_id=case.id,
        caller_name=caller_name or "Helpline 112 Caller",
        caller_phone=caller_phone or "+91-112",
        audio_file_url=file_url,
        transcript=asr_res.get("transcript"),
        language=language,
        asr_confidence=asr_res.get("asr_confidence", 0.94)
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return LostPersonReportOut.model_validate(report)


@router.post("/{id}/matches/{match_id}/verify", response_model=FaceMatchOut, summary="Verify or reject AI face match candidate")
async def verify_match(
    id: str,
    match_id: str,
    req: FaceMatchVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    match = await lost_person_service.verify_match(db, case_id=id, match_id=match_id, verified=req.verified, user_id=user_id)
    return FaceMatchOut.model_validate(match)


@router.post("/{id}/dispatch", response_model=LostPersonCaseOut, summary="Dispatch nearby volunteer squad")
async def dispatch_volunteer(
    id: str,
    volunteer_name: str = "Nearby Volunteer Squad",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.dispatch_volunteer(db, case_id=id, volunteer_name=volunteer_name, user_id=user_id)
    return LostPersonCaseOut.model_validate(case)


@router.post("/{id}/reunite", response_model=LostPersonCaseOut, summary="Mark pilgrim as reunited")
async def reunite_case(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.reunite_case(db, case_id=id, user_id=user_id)
    return LostPersonCaseOut.model_validate(case)


@router.post("/{id}/purge-sensitive-data", response_model=PurgeSensitiveDataResponse, summary="Privacy purge of case biometric vectors & audio")
async def purge_sensitive_data(id: str, db: AsyncSession = Depends(get_db)):
    """
    Permanently purge temporary biometric vectors, face search embeddings,
    and audio metadata while maintaining the minimum operational audit record.
    """
    deleted_count = await lost_person_service.purge_sensitive_data(db, case_id=id)
    return PurgeSensitiveDataResponse(
        success=True,
        message="Sensitive biometric embeddings and temporary audio references purged successfully.",
        purged_records_count=deleted_count,
        case_id=id
    )


@router.post("/{id}/pa-announce", summary="Queue Public Address Announcement")
async def queue_pa_announcement(
    id: str,
    location: str = "Wakhri Phata Loudspeaker Sector 3",
    db: AsyncSession = Depends(get_db)
):
    case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == id))).scalar_one_or_none()
    if not case:
        raise NotFoundException("Case not found")

    msg = f"हरवलेली व्यक्ती: {case.name}, वय {case.age}, पोशाख: {case.clothing_description}."
    await notification_adapter.send_pa_announcement(location, msg)
    return {
        "success": True,
        "case_number": case.case_number,
        "location": location,
        "message": "PA announcement queued for broadcast",
        "announcement_marathi": msg
    }
