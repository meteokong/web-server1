"""TokenService: create access/refresh tokens, verify, rotate.

Bridges the stateless JWT utilities (src/utils/jwt.py) with the
refresh_tokens table (src/models/refresh_token.py). A refresh token is
both a signed JWT (carrying sub/exp like any token) AND has a matching
DB row, so it can be revoked and rotation can detect reuse of a
refresh token that's already been exchanged for a new one.
"""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import UnauthorizedError
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.utils.jwt import (
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)

_INVALID_REFRESH_MESSAGE = "invalid or expired refresh token"


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class TokenService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def issue_tokens(self, user: User) -> TokenPair:
        """Issue a fresh access/refresh pair for `user` and persist the
        refresh token's hash (never the raw value) so it can later be
        verified, revoked, or rotated."""
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        expires_at = datetime.fromtimestamp(decode_refresh_token(refresh_token)["exp"], tz=UTC)
        self.db.add(
            RefreshToken(
                user_id=user.id,
                token_hash=_hash_token(refresh_token),
                expires_at=expires_at,
            )
        )
        await self.db.flush()
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def verify_access_token(self, access_token: str) -> dict:
        """Verify an access token; raises UnauthorizedError (not the raw
        JWT exceptions) so route dependencies don't need to know about
        src/utils/jwt.py's exception types."""
        try:
            return decode_access_token(access_token)
        except (TokenExpiredError, InvalidTokenError) as exc:
            raise UnauthorizedError("invalid or expired access token") from exc

    async def rotate_refresh_token(self, refresh_token: str) -> TokenPair:
        """Verify `refresh_token`, revoke its DB row, and issue a brand new
        access/refresh pair (rotate-on-use, per research.md). Raises
        UnauthorizedError if the token is invalid, expired, already
        rotated/revoked, or was never issued by this service."""
        try:
            payload = decode_refresh_token(refresh_token)
        except (TokenExpiredError, InvalidTokenError) as exc:
            raise UnauthorizedError(_INVALID_REFRESH_MESSAGE) from exc

        row = await self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == _hash_token(refresh_token))
        )
        if row is None or row.revoked:
            raise UnauthorizedError(_INVALID_REFRESH_MESSAGE)

        row.revoked = True
        row.revoked_at = datetime.now(UTC)
        await self.db.flush()

        new_access_token = create_access_token(payload["sub"])
        new_refresh_token = create_refresh_token(payload["sub"])
        new_expires_at = datetime.fromtimestamp(
            decode_refresh_token(new_refresh_token)["exp"], tz=UTC
        )
        self.db.add(
            RefreshToken(
                user_id=row.user_id,
                token_hash=_hash_token(new_refresh_token),
                expires_at=new_expires_at,
            )
        )
        await self.db.flush()
        return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)
