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

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.user import User
from src.services.auth.user_service import UserService

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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: AuthRequest, db: AsyncSession = Depends(get_db)) -> User:
    """Create a new account. Does NOT log the user in (no cookies set) —
    register and login are deliberately separate steps."""
    return await UserService(db).register(body.email, body.password)
