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

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME, get_current_user
from src.api.exceptions import ErrorDetail, ErrorResponse, UnauthorizedError
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


class MessageResponse(BaseModel):
    message: str


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


def _unauthorized_response_clearing_cookies(exc: UnauthorizedError) -> JSONResponse:
    """Build the same {"error": {...}} shape the global AppError handler
    would, but as a real Response object so delete_cookie() actually
    lands on it — a Response obtained via Depends() is thrown away by
    FastAPI once a route raises, so clearing cookies "on the way out" of
    the refresh route requires returning this instead of raising."""
    error_response = JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
        ).model_dump(exclude_none=True),
    )
    _clear_auth_cookies(error_response)
    return error_response


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


@router.post("/refresh", response_model=UserResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User | JSONResponse:
    """Not behind get_current_user: the whole point of this endpoint is
    to be callable once the access token has already expired.

    On failure this returns (rather than raises) a JSONResponse so the
    "clear both cookies, the client's refresh token is dead either way"
    part of the contract can actually attach Set-Cookie headers to the
    error response — see _unauthorized_response_clearing_cookies."""
    token_service = TokenService(db)
    try:
        if refresh_token is None:
            raise UnauthorizedError("invalid or expired refresh token")

        pair = await token_service.rotate_refresh_token(refresh_token)
        payload = token_service.verify_access_token(pair.access_token)
        user = await db.get(User, uuid.UUID(payload["sub"]))
        if user is None:
            raise UnauthorizedError("invalid or expired refresh token")
    except UnauthorizedError as exc:
        return _unauthorized_response_clearing_cookies(exc)

    _set_auth_cookies(response, pair)
    return user
