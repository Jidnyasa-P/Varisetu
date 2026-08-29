import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

# from app.core.redis import redis_client             not used since we are not using redis
from app.websocket.events import WebSocketEventType, WebSocketMessage

logger = logging.getLogger("varisetu.websocket")


class ConnectionManager:
    def __init__(self):
        # Maps channel name -> Set of connected WebSockets
        self.channels: Dict[str, Set[WebSocket]] = {
            "all": set(),
            "dashboard": set(),
            "incidents": set(),
            "crowd": set(),
            "medical": set(),
            "resources": set(),
            "lost-persons": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(websocket)
        self.channels["all"].add(websocket)
        logger.info(f"WebSocket client connected on channel: {channel} (Total: {len(self.channels['all'])})")

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.channels:
            self.channels[channel].discard(websocket)
        self.channels["all"].discard(websocket)
        logger.info(f"WebSocket client disconnected from channel: {channel}")

    async def broadcast(self, event_type: WebSocketEventType, data: dict, channel: str = "all"):
        """Broadcast typed JSON event to connected clients on the given channel."""
        message = WebSocketMessage(event=event_type, data=data)
        payload = message.model_dump_json()

        # Publish to Redis if connected
        await redis_client.publish(f"varisetu:ws:{channel}", message.model_dump())

        # Direct local broadcast to connected clients
        targets = self.channels.get(channel, set()) | self.channels.get("all", set())
        if not targets:
            return

        dead_sockets = set()
        for connection in targets:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending message to WebSocket client: {e}")
                dead_sockets.add(connection)

        # Clean up dead sockets
        for dead in dead_sockets:
            for ch in self.channels.values():
                ch.discard(dead)


ws_manager = ConnectionManager()
