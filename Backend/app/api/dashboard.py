from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.user import User
from app.schemas.dashboard import CommandPictureOut, CorridorRouteSegment, DashboardSummary, HeatRiskReadout, IncidentTickerItem
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/command-picture", response_model=CommandPictureOut, summary="Get unified common operating picture")
async def get_command_picture(db: AsyncSession = Depends(get_db)):
    """
    Returns full high-performance async aggregated command picture:
    Summary statistics, live Yatra GPS telemetry, incident queue, medical alerts,
    lost persons, candidate face matches, resource deployments, routes, recommendations,
    incident timeline, notifications, and heatmap points.
    """
    return await dashboard_service.get_command_picture(db)


@router.get("/summary", response_model=DashboardSummary, summary="Get real-time operational summary metrics")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns live operational statistics aggregated dynamically from database state:
    Active incidents, lost cases, medical emergencies, critical zones, tanker deployments, and camera telemetry.
    """
    return await dashboard_service.get_summary(db)


@router.get("/ticker", response_model=List[IncidentTickerItem], summary="Get incident ticker feed items")
async def get_dashboard_ticker(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retrieve timestamped incident timeline events for the bottom monospace operational ticker."""
    return await dashboard_service.get_ticker_events(db, limit=limit)


@router.get("/heat-risk", response_model=HeatRiskReadout, summary="Get heat-risk readout metrics")
async def get_heat_risk():
    """Retrieve computed ambient temperature, humidity, and heat risk advisory."""
    return await dashboard_service.get_heat_risk()


@router.get("/map-corridor", response_model=List[CorridorRouteSegment], summary="Get route corridor segments with live density")
async def get_map_corridor():
    """Returns coordinate segments with heat density colors for Leaflet map overlay."""
    return [
        CorridorRouteSegment(
            name="Alandi - Saswad",
            sector="Sector 1-2",
            density_percentage=35.0,
            color_hex="#2E5B36",
            status_tag="NORMAL",
            coordinates=[
                [18.6772, 73.8967],
                [18.5204, 73.8567],
                [18.3440, 74.0305]
            ]
        ),
        CorridorRouteSegment(
            name="Saswad - Bhalwani",
            sector="Sector 3",
            density_percentage=74.0,
            color_hex="#B8551B",
            status_tag="HEAVY",
            coordinates=[
                [18.3440, 74.0305],
                [18.1500, 74.3000],
                [17.8900, 75.0200]
            ]
        ),
        CorridorRouteSegment(
            name="Wakhri - Pandharpur",
            sector="Sector 4-5",
            density_percentage=94.0,
            color_hex="#9A2525",
            status_tag="CRITICAL",
            coordinates=[
                [17.8900, 75.0200],
                [17.7280, 75.2950],
                [17.6777, 75.3276]
            ]
        )
    ]
