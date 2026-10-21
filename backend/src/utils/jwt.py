"""JWT access/refresh token utilities (generate, verify, decode).

Access and refresh tokens are signed with separate secrets (see
``.env.example``: ``JWT_SECRET_KEY`` / ``JWT_REFRESH_SECRET``) so that a
leaked refresh token cannot be used to forge an access token, and vice
versa. Each token also carries a ``type`` claim as a second line of
defense against using one token type where the other is expected.
"""

import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"

TokenType = Literal["access", "refresh"]


class JWTSettings(BaseSettings):
    """JWT signing secrets and expiry, read from the environment / .env."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    jwt_secret_key: str = "dev-only-insecure-access-secret-change-me"
    jwt_refresh_secret: str = "dev-only-insecure-refresh-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


@lru_cache
def get_jwt_settings() -> JWTSettings:
    return JWTSettings()


class TokenExpiredError(Exception):
    """Raised when a token's signature is valid but it has expired."""


class InvalidTokenError(Exception):
    """Raised when a token is malformed, has a bad signature, or the wrong type."""


def _secret_for(token_type: TokenType) -> str:
    settings = get_jwt_settings()
    return settings.jwt_secret_key if token_type == "access" else settings.jwt_refresh_secret


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = get_jwt_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        # Without this, two tokens issued for the same subject within the
        # same second (iat/exp truncate to whole seconds) are byte-for-byte
        # identical strings — a real problem for refresh tokens, whose hash
        # must be unique in the DB (see TokenService.issue_tokens/rotate).
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, _secret_for(token_type), algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a short-lived access token for ``subject`` (typically the user id)."""
    settings = get_jwt_settings()
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims,
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token for ``subject`` (typically the user id)."""
    settings = get_jwt_settings()
    return _create_token(subject, "refresh", timedelta(days=settings.refresh_token_expire_days))


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """Verify signature/expiry and that ``type`` matches ``expected_type``.

    Raises ``TokenExpiredError`` or ``InvalidTokenError`` (never the raw
    PyJWT exceptions) so callers don't need to depend on PyJWT directly.
    """
    settings = get_jwt_settings()
    try:
        payload = jwt.decode(token, _secret_for(expected_type), algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError(f"{expected_type} token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError(f"{expected_type} token is invalid: {exc}") from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"expected a '{expected_type}' token, got '{payload.get('type')}'")
    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, "access")


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, "refresh")
