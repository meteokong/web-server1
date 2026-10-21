"""UserService: register, login, logout — user-identity-level auth operations.

Password hashing lives in src/utils/security.py; JWT issuance/verification
lives in TokenService (T026). This service only deals with the User's
identity and the refresh_tokens rows tied to it, not JWT claims.
"""

import re
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ConflictError, UnauthorizedError, ValidationAppError
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.utils.security import hash_password, verify_password

_MIN_PASSWORD_LENGTH = 8
# research.md: "Password requirements (min 8 chars, complexity rules)" —
# interpreted as requiring at least one letter and one digit.
_PASSWORD_HAS_LETTER_AND_DIGIT = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)")

# Same message for "no such account" and "wrong password" so a caller
# can't use the error to enumerate which emails are registered.
_INVALID_CREDENTIALS_MESSAGE = "invalid email or password"


def _validate_password_strength(password: str) -> None:
    if len(password) < _MIN_PASSWORD_LENGTH:
        raise ValidationAppError(f"password must be at least {_MIN_PASSWORD_LENGTH} characters")
    if not _PASSWORD_HAS_LETTER_AND_DIGIT.match(password):
        raise ValidationAppError("password must contain at least one letter and one digit")


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, email: str, password: str) -> User:
        """Create a new user. Raises ValidationAppError for a weak password
        or ConflictError if the email is already registered."""
        _validate_password_strength(password)

        existing = await self.db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise ConflictError("an account with this email already exists")

        user = User(email=email, password_hash=hash_password(password))
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, email: str, password: str) -> User:
        """Verify credentials and record the login. Raises UnauthorizedError
        for either an unknown email or a wrong password (same error for both —
        see _INVALID_CREDENTIALS_MESSAGE)."""
        user = await self.db.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError(_INVALID_CREDENTIALS_MESSAGE)

        user.last_login_at = datetime.now(UTC)
        await self.db.flush()
        return user

    async def logout(self, user_id) -> None:
        """End every session: revoke all of this user's active refresh tokens."""
        now = datetime.now(UTC)
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=now)
        )
        await self.db.flush()
