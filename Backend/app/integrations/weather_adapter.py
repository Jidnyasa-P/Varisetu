import os
import logging
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger("varisetu.adapters")


class WeatherAdapter:
    """Weather and heat risk index provider."""
    def __init__(self):
        self.provider = settings.WEATHER_PROVIDER

    async def get_heat_metrics(self, latitude: float, longitude: float) -> Dict[str, Any]:
        return {
            "ambient_temperature": "34° C",
            "relative_humidity": "72%",
            "computed_risk_index": "7.8 / 10 (MODERATE HEAT RISK)",
            "water_stations_active": "12 Operational",
            "orsl_sachet_supplies": "14,200 Packets Available",
            "advisory_action": "Trigger mist sprayer vans at Wakhri Junction & increase water distribution post deployment by 20%."
        }


class NotificationAdapter:
    """Outbound SMS / WhatsApp / IVR alert integration adapter."""
    def __init__(self):
        self.provider = settings.NOTIFICATION_PROVIDER

    async def send_sms(self, phone: str, message: str) -> bool:
        logger.info(f"[MOCK SMS] Sending to {phone}: {message}")
        return True

    async def send_pa_announcement(self, location: str, message: str) -> bool:
        logger.info(f"[MOCK PA] Dispatched public address announcement to {location}: {message}")
        return True


class StorageAdapter:
    """File storage interface (Local disk / Supabase Storage)."""
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.upload_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"/uploads/{filename}"

    async def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


weather_adapter = WeatherAdapter()
notification_adapter = NotificationAdapter()
storage_adapter = StorageAdapter()
