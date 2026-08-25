from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.route import Route, RouteStatus
from app.models.user import User
from app.schemas.route import RouteActionRequest, RouteCreate, RouteOut, RouteUpdate
from app.services.route_service import route_service

router = APIRouter(prefix="/routes", tags=["Routes"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[RouteOut], summary="List all monitored pilgrimage route segments")
async def list_routes(db: AsyncSession = Depends(get_db)):
    routes = await route_service.get_routes(db)
    return [RouteOut.model_validate(r) for r in routes]


@router.get("/{id}", response_model=RouteOut, summary="Get route details")
async def get_route(id: str, db: AsyncSession = Depends(get_db)):
    route = (await db.execute(select(Route).where(Route.id == id))).scalar_one_or_none()
    if not route:
        raise NotFoundException("Route not found")
    return RouteOut.model_validate(route)


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED, summary="Create new route segment")
async def create_route(route_in: RouteCreate, db: AsyncSession = Depends(get_db)):
    route = Route(**route_in.model_dump())
    db.add(route)
    await db.commit()
    await db.refresh(route)
    return RouteOut.model_validate(route)


@router.post("/{id}/divert", response_model=RouteOut, summary="Set route status to DIVERTED")
async def divert_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Diverted by Command Center"
    route = await route_service.change_status(db, id, RouteStatus.DIVERTED, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)


@router.post("/{id}/close", response_model=RouteOut, summary="Set route status to CLOSED")
async def close_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Closed due to heavy pedestrian bottleneck"
    route = await route_service.change_status(db, id, RouteStatus.CLOSED, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)


@router.post("/{id}/open", response_model=RouteOut, summary="Set route status to OPEN")
async def open_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Corridor cleared for pilgrims"
    route = await route_service.change_status(db, id, RouteStatus.OPEN, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)
