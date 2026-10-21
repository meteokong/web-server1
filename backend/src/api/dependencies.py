"""Authentication dependency for route protection.

Use ``Depends(get_current_user)`` on any route that requires a logged-in
user; it reads the access token from its HTTPOnly cookie (research.md's
auth design — the token is never readable by JS), verifies it via
TokenService, and resolves it to the actual User row.
"""

import uuid

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import UnauthorizedError
from src.db.session import get_db
from src.models.user import User
from src.services.auth.token_service import TokenService

ACCESS_TOKEN_COOKIE_NAME = "access_token"

_NOT_AUTHENTICATED_MESSAGE = "not authenticated"


async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User:
    if access_token is None:
        raise UnauthorizedError(_NOT_AUTHENTICATED_MESSAGE)

    payload = TokenService(db).verify_access_token(access_token)

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError(_NOT_AUTHENTICATED_MESSAGE) from exc

    user = await db.get(User, user_id)
    if user is None:
        raise UnauthorizedError(_NOT_AUTHENTICATED_MESSAGE)

    return user
