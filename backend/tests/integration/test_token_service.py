"""Integration tests for TokenService — run against the real database
(see tests/conftest.py's db_session fixture) because what matters here
(the refresh_tokens row actually being persisted with a hash rather
than the raw token, rotation revoking the old row, reuse of a rotated
token being rejected) are DB-level guarantees a mocked session can't prove.
"""

import hashlib

import pytest
from sqlalchemy import select

from src.api.exceptions import UnauthorizedError
from src.models.refresh_token import RefreshToken
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService


async def _make_user(db_session, email="token-test@example.com"):
    return await UserService(db_session).register(email, "correct-horse-123")


async def test_issue_tokens_returns_a_pair_and_persists_hashed_refresh_token(db_session):
    user = await _make_user(db_session)
    service = TokenService(db_session)

    pair = await service.issue_tokens(user)

    assert pair.access_token
    assert pair.refresh_token
    assert pair.access_token != pair.refresh_token

    expected_hash = hashlib.sha256(pair.refresh_token.encode("utf-8")).hexdigest()
    row = await db_session.scalar(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    assert row is not None
    assert row.token_hash == expected_hash
    # The raw token must never be stored, only its hash.
    assert row.token_hash != pair.refresh_token
    assert row.revoked is False


async def test_verify_access_token_returns_payload_for_valid_token(db_session):
    user = await _make_user(db_session, "verify-ok@example.com")
    service = TokenService(db_session)
    pair = await service.issue_tokens(user)

    payload = service.verify_access_token(pair.access_token)
    assert payload["sub"] == str(user.id)


def test_verify_access_token_rejects_garbage_token(db_session):
    service = TokenService(db_session)
    with pytest.raises(UnauthorizedError):
        service.verify_access_token("not-a-real-token")


async def test_verify_access_token_rejects_a_refresh_token(db_session):
    """A refresh token must not work as an access token (type confusion)."""
    user = await _make_user(db_session, "verify-wrong-type@example.com")
    service = TokenService(db_session)
    pair = await service.issue_tokens(user)

    with pytest.raises(UnauthorizedError):
        service.verify_access_token(pair.refresh_token)


async def test_rotate_refresh_token_issues_new_pair_and_revokes_old_row(db_session):
    user = await _make_user(db_session, "rotate-ok@example.com")
    service = TokenService(db_session)
    first_pair = await service.issue_tokens(user)

    new_pair = await service.rotate_refresh_token(first_pair.refresh_token)

    assert new_pair.refresh_token != first_pair.refresh_token
    assert new_pair.access_token != first_pair.access_token

    old_hash = hashlib.sha256(first_pair.refresh_token.encode("utf-8")).hexdigest()
    old_row = await db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == old_hash)
    )
    assert old_row.revoked is True

    new_hash = hashlib.sha256(new_pair.refresh_token.encode("utf-8")).hexdigest()
    new_row = await db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == new_hash)
    )
    assert new_row is not None
    assert new_row.revoked is False


async def test_rotate_rejects_reuse_of_an_already_rotated_token(db_session):
    """Security property: once a refresh token has been rotated, using
    that same (now-stale) token again must fail — otherwise a stolen
    token remains usable forever even after the legitimate client rotated it."""
    user = await _make_user(db_session, "rotate-reuse@example.com")
    service = TokenService(db_session)
    first_pair = await service.issue_tokens(user)

    await service.rotate_refresh_token(first_pair.refresh_token)

    with pytest.raises(UnauthorizedError):
        await service.rotate_refresh_token(first_pair.refresh_token)


async def test_rotate_rejects_garbage_token(db_session):
    service = TokenService(db_session)
    with pytest.raises(UnauthorizedError):
        await service.rotate_refresh_token("not-a-real-token")


async def test_rotate_rejects_unknown_but_well_signed_token(db_session):
    """A syntactically valid refresh token that was never issued (not in
    the DB) must be rejected — tests the DB lookup, not just JWT verification."""
    from src.utils.jwt import create_refresh_token

    service = TokenService(db_session)
    never_issued = create_refresh_token("00000000-0000-0000-0000-000000000000")

    with pytest.raises(UnauthorizedError):
        await service.rotate_refresh_token(never_issued)
