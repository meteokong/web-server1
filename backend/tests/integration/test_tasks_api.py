"""Integration tests for the Tasks API (T070-T075): list/create tasks
under a project, and get/patch/delete/code for a single task. Driven
against the real FastAPI app via the shared ``auth_client`` fixture
(see tests/integration/test_projects_api.py for the exact pattern).
"""

import uuid

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService


async def _login(db_session, client, email: str):
    user = await UserService(db_session).register(email, "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)
    client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.access_token)
    return user


# ---------------------------------------------------------------------------
# GET /api/v1/projects/{project_id}/tasks (T070)
# ---------------------------------------------------------------------------


async def test_list_tasks_returns_only_this_projects_active_tasks(auth_client, db_session):
    user = await _login(db_session, auth_client, "list-ok@example.com")
    project = await ProjectService(db_session).create(user.id, "Project")
    other_project = await ProjectService(db_session).create(user.id, "Other Project")
    task_service = TaskService(db_session)
    kept = await task_service.create(project.id, user.id, "Keep This Task")
    trashed = await task_service.create(project.id, user.id, "Trash This Task")
    await task_service.soft_delete(trashed.id, user.id)
    await task_service.create(other_project.id, user.id, "Not In This Project")

    response = await auth_client.get(f"/api/v1/projects/{project.id}/tasks")

    assert response.status_code == 200
    body = response.json()
    assert [t["id"] for t in body["tasks"]] == [str(kept.id)]


async def test_list_tasks_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register("list-noauth@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(user.id, "Project")

    response = await auth_client.get(f"/api/v1/projects/{project.id}/tasks")

    assert response.status_code == 401


async def test_list_tasks_404_for_unknown_project(auth_client, db_session):
    await _login(db_session, auth_client, "list-unknown@example.com")

    response = await auth_client.get(f"/api/v1/projects/{uuid.uuid4()}/tasks")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_list_tasks_404_for_another_users_project(auth_client, db_session):
    owner = await UserService(db_session).register("list-owner@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(owner.id, "Not Yours")
    await _login(db_session, auth_client, "list-stranger@example.com")

    response = await auth_client.get(f"/api/v1/projects/{project.id}/tasks")

    assert response.status_code == 404
