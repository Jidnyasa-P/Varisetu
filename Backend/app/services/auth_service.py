from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut
from app.services.audit_service import audit_service


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> TokenResponse:
        query = select(User).where(User.email == login_data.email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        await audit_service.log_action(
            db=db,
            action="USER_LOGIN",
            entity_type="User",
            entity_id=user.id,
            user_id=user.id
        )
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        user_id = payload.get("sub")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found or inactive")

        access_token = create_access_token(subject=user.id, role=user.role.value)
        new_refresh = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserCreate) -> UserOut:
        existing = await db.execute(select(User).where(User.email == user_in.email))
        if existing.scalar_one_or_none():
            raise ConflictException(f"User with email {user_in.email} already exists")

        new_user = User(
            name=user_in.name,
            email=user_in.email,
            phone=user_in.phone,
            password_hash=get_password_hash(user_in.password),
            role=user_in.role,
            department=user_in.department,
            is_active=user_in.is_active
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        await audit_service.log_action(
            db=db,
            action="USER_REGISTERED",
            entity_type="User",
            entity_id=new_user.id
        )
        return UserOut.model_validate(new_user)

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[UserOut]:
        query = select(User).order_by(User.name)
        result = await db.execute(query)
        users = result.scalars().all()
        return [UserOut.model_validate(u) for u in users]


auth_service = AuthService()
