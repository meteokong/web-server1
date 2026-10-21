"""Integration tests for UserService — run against the real database
(see tests/conftest.py's db_session fixture) because the behaviors that
matter here (duplicate-email rejection, password hash never round-tripping
to plaintext, last_login_at actually persisting) are DB-level guarantees,
not something a mocked session would prove.
"""

import pytest
from sqlalchemy import select

from src.api.exceptions import ConflictError, UnauthorizedError, ValidationAppError
from src.models.refresh_token import RefreshToken
from src.services.auth.user_service import UserService


async def test_register_creates_user_with_hashed_password(db_session):
    service = UserService(db_session)
    user = await service.register("register-ok@example.com", "correct-horse-123")

    assert user.email == "register-ok@example.com"
    assert user.password_hash != "correct-horse-123"
    assert user.id is not None


async def test_register_rejects_duplicate_email(db_session):
    service = UserService(db_session)
    await service.register("dup@example.com", "correct-horse-123")

    with pytest.raises(ConflictError):
        await service.register("dup@example.com", "another-password-1")


@pytest.mark.parametrize(
    "password",
    [
        "short1",  # under 8 chars
        "alllettersnodigit",  # no digit
        "12345678",  # no letter
    ],
)
async def test_register_rejects_weak_password(db_session, password):
    service = UserService(db_session)
    with pytest.raises(ValidationAppError):
        await service.register("weak-pw@example.com", password)


async def test_login_succeeds_with_correct_credentials_and_updates_last_login(db_session):
    service = UserService(db_session)
    registered = await service.register("login-ok@example.com", "correct-horse-123")
    assert registered.last_login_at is None

    logged_in = await service.login("login-ok@example.com", "correct-horse-123")
    assert logged_in.id == registered.id
    assert logged_in.last_login_at is not None


async def test_login_fails_with_wrong_password(db_session):
    service = UserService(db_session)
    await service.register("login-wrong-pw@example.com", "correct-horse-123")

    with pytest.raises(UnauthorizedError):
        await service.login("login-wrong-pw@example.com", "totally-wrong-1")


async def test_login_fails_for_nonexistent_email_same_error_as_wrong_password(db_session):
    """Must raise the identical error as a wrong password — a different
    error (or message) for 'email not found' vs 'wrong password' lets an
    attacker enumerate which emails are registered."""
    service = UserService(db_session)

    with pytest.raises(UnauthorizedError) as exc_info:
        await service.login("does-not-exist@example.com", "whatever-123")

    await service.register("enum-check@example.com", "correct-horse-123")
    with pytest.raises(UnauthorizedError) as exc_info_2:
        await service.login("enum-check@example.com", "wrong-password-1")

    assert str(exc_info.value) == str(exc_info_2.value)


async def test_logout_revokes_all_active_refresh_tokens_for_user(db_session):
    from datetime import UTC, datetime, timedelta

    service = UserService(db_session)
    user = await service.register("logout-test@example.com", "correct-horse-123")

    token1 = RefreshToken(
        user_id=user.id,
        token_hash="hash-1",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    token2 = RefreshToken(
        user_id=user.id,
        token_hash="hash-2",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add_all([token1, token2])
    await db_session.flush()

    await service.logout(user.id)

    result = await db_session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    tokens = result.scalars().all()
    assert len(tokens) == 2
    assert all(t.revoked is True for t in tokens)
    assert all(t.revoked_at is not None for t in tokens)
