"""Integration tests for DocumentQueueService (T095) — run against the
real database (see tests/conftest.py's db_session fixture), because the
behaviors that matter (LearningDocument row created/reused,
celery_task_id persisted, generation_status read back) are DB-level
guarantees.

``enqueue`` is tested with a fake dispatch callable injected via the
constructor (mimicking Celery's ``.delay()`` return value: an object with
an ``.id`` attribute) so these tests never touch a real Celery broker —
see src/tasks/document_generation.py (T094) for the real task this stands
in for.
"""

import pytest

from src.api.exceptions import NotFoundError
from src.models.learning_document import LearningDocument
from src.models.user import User
from src.services.document.document_queue_service import DocumentQueueService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils.security import hash_password


class _FakeAsyncResult:
    def __init__(self, task_id: str):
        self.id = task_id


class _FakeDispatcher:
    """Stands in for ``generate_document_task.delay`` — records calls and
    returns a fake AsyncResult-like object without touching a broker."""

    def __init__(self, celery_task_id: str = "fake-celery-task-id"):
        self.calls: list[tuple[str, str]] = []
        self._celery_task_id = celery_task_id

    def __call__(self, task_id: str, user_id: str) -> _FakeAsyncResult:
        self.calls.append((task_id, user_id))
        return _FakeAsyncResult(self._celery_task_id)


async def _make_task(db_session, email: str):
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")
    return user, task


# ---------------------------------------------------------------------------
# enqueue()
# ---------------------------------------------------------------------------


async def test_enqueue_creates_pending_document_and_dispatches(db_session):
    user, task = await _make_task(db_session, "queue-ok@example.com")
    dispatcher = _FakeDispatcher("celery-task-abc")
    service = DocumentQueueService(db_session, dispatch=dispatcher)

    document = await service.enqueue(task.id, user.id)

    assert document.task_id == task.id
    assert document.generation_status == "pending"
    assert document.celery_task_id == "celery-task-abc"
    assert dispatcher.calls == [(str(task.id), str(user.id))]


async def test_enqueue_reuses_existing_document_row_without_duplicate(db_session):
    user, task = await _make_task(db_session, "queue-reuse@example.com")
    service = DocumentQueueService(db_session, dispatch=_FakeDispatcher("first"))
    first = await service.enqueue(task.id, user.id)

    service2 = DocumentQueueService(db_session, dispatch=_FakeDispatcher("second"))
    second = await service2.enqueue(task.id, user.id)

    assert first.id == second.id
    assert second.celery_task_id == "second"

    from sqlalchemy import select

    result = await db_session.execute(
        select(LearningDocument).where(LearningDocument.task_id == task.id)
    )
    assert len(result.scalars().all()) == 1


async def test_enqueue_raises_not_found_when_task_has_no_owner_match(db_session):
    user, task = await _make_task(db_session, "queue-owner@example.com")
    stranger = User(email="queue-stranger@example.com", password_hash=hash_password("x"))
    db_session.add(stranger)
    await db_session.flush()
    service = DocumentQueueService(db_session, dispatch=_FakeDispatcher())

    with pytest.raises(NotFoundError):
        await service.enqueue(task.id, stranger.id)


# ---------------------------------------------------------------------------
# get_status()
# ---------------------------------------------------------------------------


async def test_get_status_returns_pending_with_nulls_when_no_document_exists(db_session):
    user, task = await _make_task(db_session, "status-none@example.com")
    service = DocumentQueueService(db_session, dispatch=_FakeDispatcher())

    status = await service.get_status(task.id, user.id)

    assert status == {
        "task_id": task.id,
        "generation_status": "pending",
        "generation_error": None,
        "generation_started_at": None,
        "generation_completed_at": None,
    }


async def test_get_status_returns_existing_document_fields(db_session):
    user, task = await _make_task(db_session, "status-ok@example.com")
    service = DocumentQueueService(db_session, dispatch=_FakeDispatcher("celery-xyz"))
    await service.enqueue(task.id, user.id)

    status = await service.get_status(task.id, user.id)

    assert status["task_id"] == task.id
    assert status["generation_status"] == "pending"
    assert status["generation_error"] is None


async def test_get_status_raises_not_found_for_non_owner(db_session):
    user, task = await _make_task(db_session, "status-stranger@example.com")
    stranger = User(email="status-stranger2@example.com", password_hash=hash_password("x"))
    db_session.add(stranger)
    await db_session.flush()
    service = DocumentQueueService(db_session, dispatch=_FakeDispatcher())

    with pytest.raises(NotFoundError):
        await service.get_status(task.id, stranger.id)
