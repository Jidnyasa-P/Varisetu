import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserRole, get_current_user, require_roles
from app.models.user import User
from app.schemas.action import ActionCreate, ActionOut
from app.services.action_service import action_service

logger = logging.getLogger("varisetu.api.actions")
router = APIRouter(prefix="/actions", tags=["Action Layer"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ActionOut, status_code=201, summary="Execute operational command action")
async def execute_action(
    action_in: ActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes a high-impact operational command action (Dispatch, Route Change, Verification, Resolution).
    Enforces server-side idempotency, atomic DB transaction, audit logging, and realtime WebSocket event broadcast.
    """
    # RBAC action-level authorization validation
    role = current_user.role
    if action_in.action_type in ["CHANGE_ROUTE", "QUEUE_PA_ANNOUNCEMENT", "BROADCAST_PUBLIC_ALERT"]:
        if role not in [UserRole.ADMIN, UserRole.COMMANDER]:
            raise HTTPException(status_code=403, detail="Only Admin or Commander can authorize route diversions and public alerts")
    elif action_in.action_type in ["DISPATCH_AMBULANCE", "DISPATCH_MEDICAL_VAN"]:
        if role not in [UserRole.ADMIN, UserRole.COMMANDER, UserRole.MEDICAL]:
            raise HTTPException(status_code=403, detail="Only Medical Team or Commander can dispatch ambulances")
    elif action_in.action_type in ["DISPATCH_POLICE", "DISPATCH_VOLUNTEER"]:
        if role not in [UserRole.ADMIN, UserRole.COMMANDER, UserRole.POLICE, UserRole.VOLUNTEER_COORDINATOR]:
            raise HTTPException(status_code=403, detail="Unauthorized to dispatch security personnel")

    action = await action_service.execute_action(
        db=db,
        action_in=action_in,
        user_id=current_user.id,
        user_role=current_user.role
    )
    return action


@router.get("", response_model=List[ActionOut], summary="List recent operational actions")
async def list_actions(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List recent command actions with execution status and target results."""
    return await action_service.list_actions(db, limit=limit)
