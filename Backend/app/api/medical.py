from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.medical import MedicalAlert, MedicalAlertStatus
from app.models.user import User
from app.schemas.medical import (
    MedicalAlertAcknowledgeRequest,
    MedicalAlertCreate,
    MedicalAlertDispatchRequest,
    MedicalAlertOut,
    MedicalAlertResolveRequest
)
from app.services.medical_service import medical_service

router = APIRouter(prefix="/medical-alerts", tags=["Medical Alerts"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[MedicalAlertOut], summary="List active & resolved medical alerts")
async def list_medical_alerts(
    status: Optional[MedicalAlertStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    alerts = await medical_service.get_alerts(db, status=status)
    return [MedicalAlertOut.model_validate(a) for a in alerts]


@router.post("", response_model=MedicalAlertOut, status_code=status.HTTP_201_CREATED, summary="Create medical emergency alert")
async def create_medical_alert(
    alert_in: MedicalAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.create_alert(db, alert_in, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)


@router.get("/{id}", response_model=MedicalAlertOut, summary="Get medical alert details")
async def get_medical_alert(id: str, db: AsyncSession = Depends(get_db)):
    alert = (await db.execute(select(MedicalAlert).where((MedicalAlert.id == id) | (MedicalAlert.alert_code == id)))).scalar_one_or_none()
    if not alert:
        raise NotFoundException("Medical alert not found")
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/acknowledge", response_model=MedicalAlertOut, summary="Acknowledge medical alert")
async def acknowledge_medical_alert(
    id: str,
    ack_req: Optional[MedicalAlertAcknowledgeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    vol_name = ack_req.assigned_volunteer_name if ack_req else None
    alert = await medical_service.acknowledge_alert(db, alert_id=id, volunteer_name=vol_name, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/dispatch", response_model=MedicalAlertOut, summary="Dispatch mobile medical van / ambulance")
async def dispatch_medical_unit(
    id: str,
    dispatch_req: MedicalAlertDispatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.dispatch_medical_unit(
        db,
        alert_id=id,
        resource_id=dispatch_req.resource_id,
        volunteer_name=dispatch_req.volunteer_name,
        user_id=user_id
    )
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/resolve", response_model=MedicalAlertOut, summary="Mark medical alert as resolved")
async def resolve_medical_alert(
    id: str,
    resolve_req: MedicalAlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.resolve_alert(db, alert_id=id, resolution_notes=resolve_req.resolution_notes, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)
