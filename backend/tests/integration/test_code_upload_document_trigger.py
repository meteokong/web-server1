"""Integration tests for T096: CodeUploadService.upload() triggers async
document generation (via DocumentQueueService.enqueue(), T095) right
after a successful upload.

Why CodeUploadService (not TaskService, despite tasks.md's wording) —
see docs/task-reports/TASK-096-*.md "기술 결정": TaskService has no
knowledge of uploads at all; CodeUploadService is the thing that actually
knows "an upload just succeeded for this task", so it's the natural place
to trigger what follows from that fact.

Most tests here inject a fake ``enqueue_document_generation`` callable
(constructor param) so they never touch Celery/Redis — this is also how
T096 keeps the *existing* CodeUploadService tests
(tests/integration/test_code_upload_service.py) passing unmodified: they
construct CodeUploadService without that param, which is exactly the
scenario the one real-wiring test below covers instead.
"""

import pytest

from src.models.learning_document import LearningDocument
from src.models.user import User
from src.services.code_analysis.code_upload_service import CodeUploadService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils.security import hash_password


async def _make_task(db_session, email: str):
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")
    return user, task


async def test_upload_calls_injected_enqueue_callable_with_task_and_user(db_session, tmp_path):
    user, task = await _make_task(db_session, "trigger-ok@example.com")
    calls = []

    async def fake_enqueue(task_id, user_id):
        calls.append((task_id, user_id))

    service = CodeUploadService(
        db_session, upload_root=tmp_path, enqueue_document_generation=fake_enqueue
    )

    await service.upload(task.id, user.id, "file", files=[("main.py", None, b"x = 1\n")])

    assert calls == [(task.id, user.id)]


async def test_upload_does_not_trigger_generation_when_upload_fails_validation(db_session, tmp_path):
    user, task = await _make_task(db_session, "trigger-badext@example.com")
    calls = []

    async def fake_enqueue(task_id, user_id):
        calls.append((task_id, user_id))

    service = CodeUploadService(
        db_session, upload_root=tmp_path, enqueue_document_generation=fake_enqueue
    )

    from src.api.exceptions import ValidationAppError

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "file", files=[("image.png", None, b"\x89PNG\r\n")])

    assert calls == []


async def test_upload_without_injected_enqueue_uses_real_document_queue_service(db_session, tmp_path):
    # No enqueue_document_generation given -> CodeUploadService wires up
    # the real DocumentQueueService(db).enqueue by default, which
    # dispatches to the real Celery task (T094) over the local Redis
    # broker (no worker consumes it in this test, so no real Gemini call
    # ever happens) and persists a LearningDocument row.
    user, task = await _make_task(db_session, "trigger-real@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    await service.upload(task.id, user.id, "file", files=[("main.py", None, b"x = 1\n")])

    from sqlalchemy import select

    result = await db_session.execute(
        select(LearningDocument).where(LearningDocument.task_id == task.id)
    )
    document = result.scalar_one()
    assert document.generation_status == "pending"
    assert document.celery_task_id is not None
