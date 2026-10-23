"""Unit tests for the UploadedCode SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`uploaded_code` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.uploaded_code import UploadedCode


def test_tablename_is_uploaded_code():
    assert UploadedCode.__tablename__ == "uploaded_code"


def test_has_expected_columns():
    columns = UploadedCode.__table__.columns
    expected = {
        "id",
        "task_id",
        "detected_language",
        "complexity_level",
        "total_lines",
        "total_files",
        "upload_size_bytes",
        "created_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert UploadedCode.__table__.columns["id"].primary_key is True


def test_task_id_is_unique_foreign_key_to_tasks_not_nullable():
    task_id_col = UploadedCode.__table__.columns["task_id"]
    assert task_id_col.nullable is False
    assert task_id_col.unique is True
    fk_targets = {fk.target_fullname for fk in task_id_col.foreign_keys}
    assert "tasks.id" in fk_targets


def test_instantiation_sets_given_fields():
    import uuid

    task_id = uuid.uuid4()
    uploaded_code = UploadedCode(
        task_id=task_id,
        detected_language="python",
        complexity_level="beginner",
        total_lines=120,
        total_files=3,
        upload_size_bytes=4096,
    )
    assert uploaded_code.task_id == task_id
    assert uploaded_code.detected_language == "python"
    assert uploaded_code.complexity_level == "beginner"
    assert uploaded_code.total_lines == 120
    assert uploaded_code.total_files == 3
    assert uploaded_code.upload_size_bytes == 4096
