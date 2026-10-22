"""Integration tests for the Documents API (T097/T098): GET
/tasks/{task_id}/document and GET /tasks/{task_id}/document/status.
Driven against the real FastAPI app via the shared ``auth_client``
fixture (see tests/integration/test_tasks_api.py for the exact pattern).

Response contract (frontend is integrating against this exact shape, see
the T094-T098 brief in docs/task-reports/TASK-097-*.md "기술 결정"):

    GET .../document/status -> {task_id, generation_status,
        generation_error, generation_started_at, generation_completed_at}
    GET .../document -> {task_id, generation_status, generation_error,
        content}  (content only non-null when generation_status=="completed")

Both require auth (401 without it) and 404 for a task that doesn't exist
or isn't owned by the current user.
"""

import uuid
from datetime import UTC, datetime

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME
from src.models.learning_document import LearningDocument
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService

SAMPLE_CONTENT = {
    "chapter1": {"title": "What This Code Does"},
    "chapter2": {},
    "chapter3": {},
    "chapter4": {},
    "chapter5": {},
    "chapter6": {},
    "chapter7": {},
}


async def _login(db_session, client, email: str):
    user = await UserService(db_session).register(email, "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)
    client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.access_token)
    return user


async def _make_task(db_session, user):
    project = await ProjectService(db_session).create(user.id, "Project")
    return await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")


# ---------------------------------------------------------------------------
# GET /api/v1/tasks/{task_id}/document/status (T098)
# ---------------------------------------------------------------------------


async def test_get_status_returns_pending_when_no_document_row_exists(auth_client, db_session):
    user = await _login(db_session, auth_client, "status-pending@example.com")
    task = await _make_task(db_session, user)

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document/status")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "task_id": str(task.id),
        "generation_status": "pending",
        "generation_error": None,
        "generation_started_at": None,
        "generation_completed_at": None,
    }


async def test_get_status_returns_completed_document_fields(auth_client, db_session):
    user = await _login(db_session, auth_client, "status-completed@example.com")
    task = await _make_task(db_session, user)
    started = datetime(2026, 10, 22, 1, 0, tzinfo=UTC)
    completed = datetime(2026, 10, 22, 1, 2, tzinfo=UTC)
    db_session.add(
        LearningDocument(
            task_id=task.id,
            content=SAMPLE_CONTENT,
            generation_status="completed",
            generation_started_at=started,
            generation_completed_at=completed,
        )
    )
    await db_session.flush()

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document/status")

    assert response.status_code == 200
    body = response.json()
    assert body["generation_status"] == "completed"
    assert body["generation_error"] is None
    assert body["generation_started_at"] is not None
    assert body["generation_completed_at"] is not None


async def test_get_status_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register("status-noauth@example.com", "correct-horse-123")
    task = await _make_task(db_session, user)

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document/status")

    assert response.status_code == 401


async def test_get_status_404_for_unknown_task(auth_client, db_session):
    await _login(db_session, auth_client, "status-unknown@example.com")

    response = await auth_client.get(f"/api/v1/tasks/{uuid.uuid4()}/document/status")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_get_status_404_for_another_users_task(auth_client, db_session):
    owner = await UserService(db_session).register("status-owner@example.com", "correct-horse-123")
    task = await _make_task(db_session, owner)
    await _login(db_session, auth_client, "status-stranger@example.com")

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document/status")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# GET /api/v1/tasks/{task_id}/document (T097)
# ---------------------------------------------------------------------------


async def test_get_document_returns_null_content_when_pending(auth_client, db_session):
    user = await _login(db_session, auth_client, "doc-pending@example.com")
    task = await _make_task(db_session, user)

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "task_id": str(task.id),
        "generation_status": "pending",
        "generation_error": None,
        "content": None,
    }


async def test_get_document_returns_content_when_completed(auth_client, db_session):
    user = await _login(db_session, auth_client, "doc-completed@example.com")
    task = await _make_task(db_session, user)
    db_session.add(
        LearningDocument(task_id=task.id, content=SAMPLE_CONTENT, generation_status="completed")
    )
    await db_session.flush()

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 200
    body = response.json()
    assert body["generation_status"] == "completed"
    assert body["content"] == SAMPLE_CONTENT


async def test_get_document_hides_content_when_in_progress(auth_client, db_session):
    user = await _login(db_session, auth_client, "doc-inprogress@example.com")
    task = await _make_task(db_session, user)
    db_session.add(
        LearningDocument(
            task_id=task.id,
            content={k: None for k in SAMPLE_CONTENT},
            generation_status="in_progress",
        )
    )
    await db_session.flush()

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 200
    body = response.json()
    assert body["generation_status"] == "in_progress"
    assert body["content"] is None


async def test_get_document_exposes_generation_error_when_failed(auth_client, db_session):
    user = await _login(db_session, auth_client, "doc-failed@example.com")
    task = await _make_task(db_session, user)
    db_session.add(
        LearningDocument(
            task_id=task.id,
            content={k: None for k in SAMPLE_CONTENT},
            generation_status="failed",
            generation_error="Gemini kept failing",
        )
    )
    await db_session.flush()

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 200
    body = response.json()
    assert body["generation_status"] == "failed"
    assert body["generation_error"] == "Gemini kept failing"
    assert body["content"] is None


async def test_get_document_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register("doc-noauth@example.com", "correct-horse-123")
    task = await _make_task(db_session, user)

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 401


async def test_get_document_404_for_unknown_task(auth_client, db_session):
    await _login(db_session, auth_client, "doc-unknown@example.com")

    response = await auth_client.get(f"/api/v1/tasks/{uuid.uuid4()}/document")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_get_document_404_for_another_users_task(auth_client, db_session):
    owner = await UserService(db_session).register("doc-owner@example.com", "correct-horse-123")
    task = await _make_task(db_session, owner)
    await _login(db_session, auth_client, "doc-stranger@example.com")

    response = await auth_client.get(f"/api/v1/tasks/{task.id}/document")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
