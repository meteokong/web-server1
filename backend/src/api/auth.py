"""Auth API endpoints (T028-T031): register, login, me, logout, refresh.

Route handlers are intentionally thin — they delegate to UserService /
TokenService (the actual business logic) and let the global exception
handlers in src/api/exceptions.py turn any AppError subclass those
services raise into the standard {"error": {...}} JSON response. See
specs/001-ai-code-learning-platform/contracts/auth-api.md for the full
contract (cookie flags, response shapes, status codes).
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME, get_current_user
from src.config import get_app_settings
from src.db.session import get_db
from src.models.user import User
from src.services.auth.token_service import TokenPair, TokenService
from src.services.auth.user_service import UserService
from src.utils.jwt import get_jwt_settings

REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

router = APIRouter()


class AuthRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    skill_level: str | None
    created_at: datetime | None


def _cookie_flags() -> dict:
    """Shared HTTPOnly cookie flags for both the access and refresh
    cookies (contract: samesite=strict, secure unless local development)."""
    settings = get_app_settings()
    return {
        "httponly": True,
        "samesite": "strict",
        "secure": settings.environment != "development",
    }


def _set_auth_cookies(response: Response, pair: TokenPair) -> None:
    jwt_settings = get_jwt_settings()
    flags = _cookie_flags()
    response.set_cookie(
        ACCESS_TOKEN_COOKIE_NAME,
        pair.access_token,
        max_age=jwt_settings.access_token_expire_minutes * 60,
        **flags,
    )
    response.set_cookie(
        REFRESH_TOKEN_COOKIE_NAME,
        pair.refresh_token,
        max_age=jwt_settings.refresh_token_expire_days * 24 * 60 * 60,
        **flags,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)


class MessageResponse(BaseModel):
    message: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: AuthRequest, db: AsyncSession = Depends(get_db)) -> User:
    """Create a new account. Does NOT log the user in (no cookies set) —
    register and login are deliberately separate steps."""
    return await UserService(db).register(body.email, body.password)


@router.post("/login", response_model=UserResponse)
async def login(body: AuthRequest, response: Response, db: AsyncSession = Depends(get_db)) -> User:
    user = await UserService(db).login(body.email, body.password)
    pair = await TokenService(db).issue_tokens(user)
    _set_auth_cookies(response, pair)
    return user


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await UserService(db).logout(current_user.id)
    _clear_auth_cookies(response)
    return MessageResponse(message="logged out")
