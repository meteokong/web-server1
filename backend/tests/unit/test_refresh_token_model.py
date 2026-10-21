"""Unit tests for the RefreshToken SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`refresh_tokens` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.refresh_token import RefreshToken


def test_tablename_is_refresh_tokens():
    assert RefreshToken.__tablename__ == "refresh_tokens"


def test_has_expected_columns():
    columns = RefreshToken.__table__.columns
    expected = {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "created_at",
        "revoked",
        "revoked_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert RefreshToken.__table__.columns["id"].primary_key is True


def test_user_id_is_foreign_key_to_users_not_nullable():
    user_id_col = RefreshToken.__table__.columns["user_id"]
    assert user_id_col.nullable is False
    fk_targets = {fk.target_fullname for fk in user_id_col.foreign_keys}
    assert "users.id" in fk_targets


def test_token_hash_is_unique_and_not_nullable():
    token_hash_col = RefreshToken.__table__.columns["token_hash"]
    assert token_hash_col.unique is True
    assert token_hash_col.nullable is False


def test_expires_at_is_not_nullable():
    assert RefreshToken.__table__.columns["expires_at"].nullable is False


def test_instantiation_sets_given_fields():
    import uuid

    user_id = uuid.uuid4()
    token = RefreshToken(user_id=user_id, token_hash="hashed-token", expires_at=None)
    assert token.user_id == user_id
    assert token.token_hash == "hashed-token"
