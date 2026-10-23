"""Unit tests for the Project SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`projects` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.project import Project


def test_tablename_is_projects():
    assert Project.__tablename__ == "projects"


def test_has_expected_columns():
    columns = Project.__table__.columns
    expected = {
        "id",
        "user_id",
        "title",
        "description",
        "created_at",
        "updated_at",
        "last_activity_at",
        "deletion_status",
        "trashed_at",
        "scheduled_deletion_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert Project.__table__.columns["id"].primary_key is True


def test_user_id_is_foreign_key_to_users_not_nullable():
    user_id_col = Project.__table__.columns["user_id"]
    assert user_id_col.nullable is False
    fk_targets = {fk.target_fullname for fk in user_id_col.foreign_keys}
    assert "users.id" in fk_targets


def test_title_is_not_nullable():
    assert Project.__table__.columns["title"].nullable is False


def test_deletion_status_defaults_to_active():
    assert Project.__table__.columns["deletion_status"].server_default.arg == "active"


def test_instantiation_sets_given_fields():
    import uuid

    user_id = uuid.uuid4()
    project = Project(user_id=user_id, title="My Project", description="A test project")
    assert project.user_id == user_id
    assert project.title == "My Project"
    assert project.description == "A test project"
