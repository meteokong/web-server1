"""Verifies the User <-> RefreshToken relationship() wiring added once
both models existed (T024 refactor step) — mapper configuration itself
is the risk here (typos in back_populates, wrong FK direction, etc.)."""

import uuid

from sqlalchemy.orm import configure_mappers

from src.models.refresh_token import RefreshToken
from src.models.user import User


def test_mappers_configure_without_error():
    # Raises if back_populates/relationship setup references a class or
    # attribute that doesn't exist.
    configure_mappers()


def test_user_refresh_tokens_relationship_navigable():
    user = User(id=uuid.uuid4(), email="rel-test@example.com", password_hash="x")
    token = RefreshToken(id=uuid.uuid4(), token_hash="hash-1", expires_at=None)

    user.refresh_tokens.append(token)

    assert token in user.refresh_tokens
    assert token.user is user
