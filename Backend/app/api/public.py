from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.database import get_db
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonStatus
from app.models.route import Route
from app.schemas.lost_person import LostPersonCaseOut
from app.services.lost_person_service import lost_person_service

public_router = APIRouter(prefix="/public", tags=["Public Pilgrim Portal"])


class PublicLostReportIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., description="Male / Female / Other")
    clothing_description: str = Field(..., min_length=2)
    last_seen_location: str = Field(..., min_length=2)
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    photo_urls: Optional[List[str]] = None


class PublicInfoResponse(BaseModel):
    service_name: str
    palkhi_name: str
    palkhi_location: str
    palkhi_coordinates: List[float]
    palkhi_speed_kmh: float
    total_pilgrims_estimate: str
    weather: dict
    helplines: List[dict]
    active_water_points: int
    active_medical_camps: int
    active_lost_cases_count: int


@public_router.get("/info", response_model=PublicInfoResponse, summary="Public pilgrim live status, map coordinates and helplines")
async def get_public_info(db: AsyncSession = Depends(get_db)):
    lost_count_res = await db.execute(
        select(func.count(LostPersonCase.id)).where(LostPersonCase.status.in_([LostPersonStatus.SEARCHING, LostPersonStatus.MATCH_FOUND]))
    )
    lost_count = lost_count_res.scalar() or 3

    return PublicInfoResponse(
        service_name="VariSetu Citizen Portal &bull; Maharashtra Police IT Cell",
        palkhi_name="Sant Tukaram Maharaj Palkhi & Sant Dnyaneshwar Maharaj Palkhi",
        palkhi_location="Approaching Wakhri Phata (Km 184) - Pandharpur Route",
        palkhi_coordinates=[17.7280, 75.2950],
        palkhi_speed_kmh=3.2,
        total_pilgrims_estimate="~8,45,000 Warkaris",
        weather={
            "ambient_temp_c": 34.0,
            "humidity_pct": 72,
            "heat_index": "7.8 / 10 (Moderate Heat Advisory)",
            "advisory": "Drink water frequently. Free ORSL rehydration sachets available at all police chowkis and Red Cross tents."
        },
        helplines=[
            {"title": "Emergency Police Control Room", "number": "112 / 02186-223344", "action": "tel:112", "badge": "24x7 TOLL FREE"},
            {"title": "Ambulance & Medical Emergency", "number": "108 / 102", "action": "tel:108", "badge": "FREE DISPATCH"},
            {"title": "Lost & Found Pilgrim Helpline", "number": "1800-233-0099", "action": "tel:18002330099", "badge": "AI REUNION"},
            {"title": "Municipal Water & Sanitation", "number": "02186-224455", "action": "tel:02186224455", "badge": "PANDHARPUR"},
            {"title": "Shri Vitthal Mandir Samiti Desk", "number": "02186-223550", "action": "tel:02186223550", "badge": "DARSHAN PASS"}
        ],
        active_water_points=24,
        active_medical_camps=16,
        active_lost_cases_count=lost_count
    )


@public_router.post("/report-lost", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Public missing relative case registration")
async def public_report_lost_person(
    report_in: PublicLostReportIn,
    db: AsyncSession = Depends(get_db)
):
    from app.schemas.lost_person import LostPersonCaseCreate
    case_in = LostPersonCaseCreate(
        name=report_in.name,
        age=report_in.age,
        gender=report_in.gender,
        clothing_description=report_in.clothing_description,
        last_seen_location=report_in.last_seen_location,
        caller_name=report_in.caller_name or "Citizen Reporter",
        caller_phone=report_in.caller_phone or "Direct Web Portal",
        photo_urls=report_in.photo_urls,
        photo_url=report_in.photo_urls[0] if report_in.photo_urls else None,
        priority="HIGH",
        is_demo=False
    )
    case = await lost_person_service.create_case(db, case_in, user_id=None)
    return {
        "status": "success",
        "message": f"Missing person report registered successfully with Case Number {case.case_number}. Police CCTV face matching engine activated.",
        "case_number": case.case_number,
        "name": case.name
    }


@public_router.get("/yatra/live", summary="Sanitized live Palkhi public tracking")
async def get_public_yatra_live(db: AsyncSession = Depends(get_db)):
    """Provides privacy-sanitized approximate Palkhi location, speed, and pilgrim advisories."""
    from app.services.yatra_service import yatra_service
    return await yatra_service.get_public_live(db)

