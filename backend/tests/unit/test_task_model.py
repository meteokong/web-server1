"""Unit tests for the Task SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`tasks` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.task import Task


def test_tablename_is_tasks():
    assert Task.__tablename__ == "tasks"


def test_has_expected_columns():
    columns = Task.__table__.columns
    expected = {
        "id",
        "project_id",
        "task_number",
        "title",
        "description",
        "upload_method",
        "created_at",
        "updated_at",
        "deletion_status",
        "trashed_at",
        "scheduled_deletion_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert Task.__table__.columns["id"].primary_key is True


def test_project_id_is_foreign_key_to_projects_not_nullable():
    project_id_col = Task.__table__.columns["project_id"]
    assert project_id_col.nullable is False
    fk_targets = {fk.target_fullname for fk in project_id_col.foreign_keys}
    assert "projects.id" in fk_targets


def test_task_number_is_not_nullable():
    assert Task.__table__.columns["task_number"].nullable is False


def test_title_is_not_nullable():
    assert Task.__table__.columns["title"].nullable is False


def test_deletion_status_defaults_to_active():
    assert Task.__table__.columns["deletion_status"].server_default.arg == "active"


def test_instantiation_sets_given_fields():
    import uuid

    project_id = uuid.uuid4()
    task = Task(
        project_id=project_id,
        task_number=1,
        title="My First Task",
        upload_method="file",
    )
    assert task.project_id == project_id
    assert task.task_number == 1
    assert task.title == "My First Task"
    assert task.upload_method == "file"
