import enum
from typing import List, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_token


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    COMMANDER = "COMMANDER"
    POLICE = "POLICE"
    MEDICAL = "MEDICAL"
    RESOURCE_MANAGER = "RESOURCE_MANAGER"
    VOLUNTEER_COORDINATOR = "VOLUNTEER_COORDINATOR"
    VIEWER = "VIEWER"


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Extracts user from JWT token if present.
    If AUTH_REQUIRED is False and no token is passed, returns a default mock Commander user.
    """
    from app.models.user import User

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            query = select(User).where(User.id == user_id, User.is_active == True)
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user

    if not settings.AUTH_REQUIRED:
        # Return a fallback admin/commander user object for development prototyping
        return User(
            id="00000000-0000-0000-0000-000000000001",
            name="Command Center Controller",
            email="control.room@mahapolice.gov.in",
            role=UserRole.ADMIN,
            department="Maharashtra Police IT Cell",
            is_active=True
        )

    return None


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Strictly requires an authenticated user."""
    user = await get_current_user_optional(authorization, db)
    if not user:
        raise UnauthorizedException("Valid authentication credentials required")
    return user


def require_roles(allowed_roles: List[UserRole]):
    """Role-based authorization dependency factory."""
    async def role_checker(current_user = Depends(get_current_user)):
        if current_user.role == UserRole.ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Role {current_user.role} does not have permission for this operation"
            )
        return current_user
    return role_checker
