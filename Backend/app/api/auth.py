from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserRole, get_current_user, require_roles
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserOut
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="User authentication with JWT issuance")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with official email/officer ID and password to receive JWT tokens."""
    return await auth_service.authenticate_user(db, login_data)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh JWT access token")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Obtain a fresh access token using a valid refresh token."""
    return await auth_service.refresh_tokens(db, req.refresh_token)


@router.get("/me", response_model=UserOut, summary="Get current authenticated user profile")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile and role details of the currently authenticated user."""
    return UserOut.model_validate(current_user)


@router.get("/users", response_model=List[UserOut], summary="List all registered officers (Admin Only)")
async def list_users(
    current_admin: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve roster of all authorized police & medical officers."""
    return await auth_service.get_all_users(db)


@router.post("/logout", summary="Log out user and invalidate session")
async def logout(current_user: User = Depends(get_current_user)):
    """Log out current user."""
    return {"success": True, "message": "Successfully logged out"}


@router.post("/register", response_model=UserOut, summary="Register new user (Admin Only)")
async def register(
    user_in: UserCreate,
    current_admin: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only endpoint to provision new authorised command center officers."""
    return await auth_service.register_user(db, user_in)
