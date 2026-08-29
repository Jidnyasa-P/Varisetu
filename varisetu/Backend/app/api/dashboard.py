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
    """Returns coordinate segments with heat density colors for Leaflet map overlay along NH-60 Pune to Nashik."""
    return [
        CorridorRouteSegment(
            name="Pune - Bhosari",
            sector="Sector 1",
            density_percentage=38.0,
            color_hex="#2E5B36",
            status_tag="NORMAL",
            coordinates=[
                [18.5074, 73.8077],
                [18.5300, 73.8400],
                [18.6270, 73.8470]
            ]
        ),
        CorridorRouteSegment(
            name="Bhosari - Manchar",
            sector="Sector 2",
            density_percentage=62.0,
            color_hex="#D98E2C",
            status_tag="MODERATE",
            coordinates=[
                [18.6270, 73.8470],
                [18.7180, 73.8780],
                [18.8600, 73.9100],
                [19.0060, 73.9450]
            ]
        ),
        CorridorRouteSegment(
            name="Manchar - Sangamner",
            sector="Sector 3",
            density_percentage=82.0,
            color_hex="#B8551B",
            status_tag="HEAVY",
            coordinates=[
                [19.0060, 73.9450],
                [19.1240, 73.9780],
                [19.3100, 74.0600],
                [19.5760, 74.2120]
            ]
        ),
        CorridorRouteSegment(
            name="Sangamner - Govind Nagar Nashik",
            sector="Sector 4",
            density_percentage=92.0,
            color_hex="#9A2525",
            status_tag="CRITICAL",
            coordinates=[
                [19.5760, 74.2120],
                [19.7050, 73.9900],
                [19.9700, 73.7800]
            ]
        )
    ]

