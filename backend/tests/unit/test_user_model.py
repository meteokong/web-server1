"""Unit tests for the User SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`users` table and T009's migration (backend/alembic/versions/001_initial_schema.py) —
the ORM model MUST match that schema exactly, not define its own.
"""

from src.models.user import User


def test_tablename_is_users():
    assert User.__tablename__ == "users"


def test_has_expected_columns():
    columns = User.__table__.columns
    expected = {
        "id",
        "email",
        "password_hash",
        "skill_level",
        "created_at",
        "updated_at",
        "last_login_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert User.__table__.columns["id"].primary_key is True


def test_email_is_unique_and_not_nullable():
    email_col = User.__table__.columns["email"]
    assert email_col.unique is True
    assert email_col.nullable is False


def test_password_hash_is_not_nullable():
    assert User.__table__.columns["password_hash"].nullable is False


def test_instantiation_sets_given_fields():
    user = User(email="student@example.com", password_hash="hashed-value")
    assert user.email == "student@example.com"
    assert user.password_hash == "hashed-value"
