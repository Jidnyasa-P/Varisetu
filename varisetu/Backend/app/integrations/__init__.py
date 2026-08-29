"""
Modular extensible adapters for AI, Vector DB, Speech, Vision, Weather, and Storage.
"""
from app.integrations.qdrant_adapter import qdrant_adapter
from app.integrations.vision_adapter import vision_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.weather_adapter import weather_adapter
from app.integrations.notification_adapter import notification_adapter
from app.integrations.storage_adapter import storage_adapter

__all__ = [
    "qdrant_adapter",
    "vision_adapter",
    "speech_adapter",
    "weather_adapter",
    "notification_adapter",
    "storage_adapter",
]
