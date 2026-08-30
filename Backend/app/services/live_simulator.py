"""
VariSetu Backend — live_simulator.py

Keeps crowd-density values genuinely changing in the background, so the
dashboard shows live movement without anyone needing to trigger the
scripted DemoService by hand. Reuses the existing (already correct)
CrowdService.record_observation() -> ws_manager.broadcast() -> frontend
handleLiveEvent() pipeline end-to-end — nothing else needed to change.

Mirrors DemoService's start()/stop() pattern for consistency and safe
shutdown handling.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.zone import Zone
from app.schemas.crowd import CrowdObservationCreate
from app.services.crowd_service import crowd_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.live_simulator")

# How often each zone's density is nudged. Kept moderate (not too chatty,
# not too slow) so movement is visibly "live" without spamming the DB/UI.
TICK_SECONDS = 18

# Zones drift toward this baseline over time instead of wandering forever,
# so density stays realistic rather than drifting to 0% or 100%.
BASELINE_DENSITY = 45.0
MEAN_REVERSION = 0.12   # fraction pulled back toward baseline each tick
NOISE_RANGE = 7.0       # max random nudge per tick, in percentage points

# Free-tier DB hygiene: prune observations older than this so the table
# doesn't grow unbounded on a long-running free Supabase instance.
RETENTION_HOURS = 6
PRUNE_EVERY_N_TICKS = 40


class LiveCrowdSimulator:
    def __init__(self):
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._tick_count: int = 0

    async def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Live crowd simulator started (tick={TICK_SECONDS}s).")

    async def stop(self) -> None:
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Live crowd simulator stopped.")

    async def _run_loop(self):
        try:
            while self.is_running:
                await asyncio.sleep(TICK_SECONDS)
                try:
                    await self._tick()
                except Exception as e:
                    # One bad tick should never kill the whole background loop.
                    logger.warning(f"Live simulator tick failed, continuing: {e}")
        except asyncio.CancelledError:
            logger.info("Live crowd simulator loop cancelled.")

    async def _tick(self):
        self._tick_count += 1
        async with AsyncSessionLocal() as db:
            zones = (await db.execute(select(Zone).where(Zone.is_active == True))).scalars().all()

            for zone in zones:
                latest = (
                    await db.execute(
                        select(CrowdObservation)
                        .where(CrowdObservation.zone_id == zone.id)
                        .order_by(CrowdObservation.observed_at.desc())
                        .limit(1)
                    )
                ).scalar_one_or_none()

                current = latest.density_percentage if latest else BASELINE_DENSITY

                pull = (BASELINE_DENSITY - current) * MEAN_REVERSION
                noise = random.uniform(-NOISE_RANGE, NOISE_RANGE)
                new_density = max(5.0, min(99.0, current + pull + noise))

                delta = new_density - current
                trend = CrowdTrend.RISING if delta > 1.5 else CrowdTrend.FALLING if delta < -1.5 else CrowdTrend.STABLE

                people_count = int((new_density / 100.0) * zone.capacity)

                obs = await crowd_service.record_observation(
                    db,
                    CrowdObservationCreate(
                        zone_id=zone.id,
                        density_percentage=round(new_density, 1),
                        people_count=people_count,
                        trend=trend,
                        source="LIVE_SIMULATOR",
                    ),
                )

                # Give the incident-log ticker something to say when a zone
                # crosses into a higher-risk band -- reuses the frontend's
                # existing TICKER_EVENT handling, no frontend changes needed.
                if latest and obs.risk_level != latest.risk_level and obs.risk_level.value in ("HIGH", "CRITICAL"):
                    await ws_manager.broadcast(
                        WebSocketEventType.TICKER_EVENT,
                        {
                            "text": f"[{datetime.now().strftime('%H:%M:%S')}] "
                                    f"{zone.name}: density crossed into {obs.risk_level.value} "
                                    f"({round(new_density)}%)"
                        },
                        channel="dashboard",
                    )

            if self._tick_count % PRUNE_EVERY_N_TICKS == 0:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)
                await db.execute(delete(CrowdObservation).where(CrowdObservation.observed_at < cutoff))
                await db.commit()


live_simulator = LiveCrowdSimulator()
