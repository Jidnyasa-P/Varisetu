from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserRole, get_current_user, require_roles
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementOut
from app.services.announcement_service import announcement_service

router = APIRouter(prefix="/announcements", tags=["Public Announcements"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[AnnouncementOut], summary="List announcements")
async def list_announcements(
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve list of queued, approved, and broadcast announcements."""
    return await announcement_service.list_announcements(db, limit=limit)


@router.post("", response_model=AnnouncementOut, status_code=201, summary="Queue a public announcement")
async def create_announcement(
    ann_in: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue a bilingual (Marathi & English) public safety announcement for commander review."""
    return await announcement_service.create_announcement(db, ann_in, user_id=current_user.id)


@router.post("/{id}/broadcast", response_model=AnnouncementOut, summary="Approve and broadcast announcement")
async def broadcast_announcement(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.COMMANDER]))
):
    """Commander / Admin approval to broadcast the announcement across PA systems and Public Portal."""
    try:
        return await announcement_service.approve_and_broadcast(db, id, approver_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
