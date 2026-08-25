import logging
from app.core.config import settings

logger = logging.getLogger("varisetu.notification_adapter")


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


notification_adapter = NotificationAdapter()
