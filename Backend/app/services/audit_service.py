import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

logger = logging.getLogger("varisetu.audit")


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create an immutable audit log record."""
        audit_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_entry)
        logger.info(f"AUDIT | {action} on {entity_type}:{entity_id or 'N/A'} by User:{user_id or 'SYSTEM'}")
        return audit_entry


audit_service = AuditService()
