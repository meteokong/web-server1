"""Unit tests for the LearningDocument SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`learning_documents` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.learning_document import LearningDocument


def test_tablename_is_learning_documents():
    assert LearningDocument.__tablename__ == "learning_documents"


def test_has_expected_columns():
    columns = LearningDocument.__table__.columns
    expected = {
        "id",
        "task_id",
        "content",
        "generation_status",
        "generation_started_at",
        "generation_completed_at",
        "generation_error",
        "celery_task_id",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert LearningDocument.__table__.columns["id"].primary_key is True


def test_task_id_is_unique_foreign_key_to_tasks_not_nullable():
    task_id_col = LearningDocument.__table__.columns["task_id"]
    assert task_id_col.nullable is False
    assert task_id_col.unique is True
    fk_targets = {fk.target_fullname for fk in task_id_col.foreign_keys}
    assert "tasks.id" in fk_targets


def test_content_is_not_nullable():
    assert LearningDocument.__table__.columns["content"].nullable is False


def test_instantiation_sets_given_fields():
    import uuid

    task_id = uuid.uuid4()
    content = {
        "chapter1": "intro",
        "chapter2": "setup",
        "chapter3": "core",
        "chapter4": "advanced",
        "chapter5": "testing",
        "chapter6": "deployment",
        "chapter7": "summary",
    }
    doc = LearningDocument(
        task_id=task_id,
        content=content,
        generation_status="pending",
        celery_task_id="celery-task-123",
    )
    assert doc.task_id == task_id
    assert doc.content == content
    assert doc.generation_status == "pending"
    assert doc.celery_task_id == "celery-task-123"
