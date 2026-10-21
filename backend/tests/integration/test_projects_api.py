"""Integration tests for the Projects API (T046-T050): list, create, get,
patch, delete. Driven against the real FastAPI app via the shared
``auth_client`` fixture (httpx.AsyncClient + ASGITransport, real DB
session — see tests/integration/conftest.py and tests/conftest.py's
db_session docstring for why TestClient is unsafe here).

Auth is exercised for real: a user is registered via UserService and a
real access-token cookie is issued via TokenService, mirroring
test_auth_me.py, rather than mocking get_current_user.
"""

import uuid

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService
from src.services.project_service import ProjectService


async def _login(db_session, client, email: str):
    user = await UserService(db_session).register(email, "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)
    client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.access_token)
    return user


# ---------------------------------------------------------------------------
# GET /api/v1/projects (T046)
# ---------------------------------------------------------------------------


async def test_list_projects_returns_only_current_users_active_projects(
    auth_client, db_session
):
    user = await _login(db_session, auth_client, "list-ok@example.com")
    other = await UserService(db_session).register("list-other@example.com", "correct-horse-123")
    service = ProjectService(db_session)
    await service.create(user.id, "React 학습")
    trashed = await service.create(user.id, "Trashed Project")
    await service.soft_delete(trashed.id, user.id)
    await service.create(other.id, "Someone Else's Project")

    response = await auth_client.get("/api/v1/projects")

    assert response.status_code == 200
    body = response.json()
    titles = {p["title"] for p in body["projects"]}
    assert titles == {"React 학습"}
    assert all(p["user_id"] == str(user.id) for p in body["projects"])


async def test_list_projects_rejects_missing_auth(auth_client):
    response = await auth_client.get("/api/v1/projects")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


# ---------------------------------------------------------------------------
# POST /api/v1/projects (T047)
# ---------------------------------------------------------------------------


async def test_create_project_success(auth_client, db_session):
    user = await _login(db_session, auth_client, "create-ok@example.com")

    response = await auth_client.post(
        "/api/v1/projects",
        json={"title": "My First Project", "description": "learning FastAPI"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "My First Project"
    assert body["description"] == "learning FastAPI"
    assert body["user_id"] == str(user.id)
    assert body["deletion_status"] == "active"
    assert body["trashed_at"] is None


async def test_create_project_rejects_blank_title(auth_client, db_session):
    await _login(db_session, auth_client, "create-blank@example.com")

    response = await auth_client.post("/api/v1/projects", json={"title": "   "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


async def test_create_project_rejects_missing_auth(auth_client):
    response = await auth_client.post("/api/v1/projects", json={"title": "No Auth"})

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/projects/{project_id} (T048)
# ---------------------------------------------------------------------------


async def test_get_project_success(auth_client, db_session):
    user = await _login(db_session, auth_client, "get-ok@example.com")
    project = await ProjectService(db_session).create(user.id, "Gettable Project")

    response = await auth_client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(project.id)
    assert body["title"] == "Gettable Project"


async def test_get_project_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register("get-noauth@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(user.id, "No Auth Project")

    response = await auth_client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 401


async def test_get_project_404_for_unknown_id(auth_client, db_session):
    await _login(db_session, auth_client, "get-unknown@example.com")

    response = await auth_client.get(f"/api/v1/projects/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_get_project_404_for_another_users_project(auth_client, db_session):
    owner = await UserService(db_session).register("get-owner@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(owner.id, "Not Yours")
    await _login(db_session, auth_client, "get-stranger@example.com")

    response = await auth_client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/v1/projects/{project_id} (T049)
# ---------------------------------------------------------------------------


async def test_patch_project_updates_title_and_description(auth_client, db_session):
    user = await _login(db_session, auth_client, "patch-ok@example.com")
    project = await ProjectService(db_session).create(user.id, "Old Title", "old description")

    response = await auth_client.patch(
        f"/api/v1/projects/{project.id}",
        json={"title": "New Title", "description": "new description"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New Title"
    assert body["description"] == "new description"


async def test_patch_project_partial_update_keeps_other_field(auth_client, db_session):
    user = await _login(db_session, auth_client, "patch-partial@example.com")
    project = await ProjectService(db_session).create(user.id, "Keep Me", "keep description")

    response = await auth_client.patch(
        f"/api/v1/projects/{project.id}", json={"description": "updated only"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Keep Me"
    assert body["description"] == "updated only"


async def test_patch_project_rejects_blank_title(auth_client, db_session):
    user = await _login(db_session, auth_client, "patch-blank@example.com")
    project = await ProjectService(db_session).create(user.id, "Valid Title")

    response = await auth_client.patch(f"/api/v1/projects/{project.id}", json={"title": "   "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


async def test_patch_project_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register("patch-noauth@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(user.id, "No Auth Project")

    response = await auth_client.patch(
        f"/api/v1/projects/{project.id}", json={"title": "Hijacked"}
    )

    assert response.status_code == 401


async def test_patch_project_404_for_another_users_project(auth_client, db_session):
    owner = await UserService(db_session).register("patch-owner@example.com", "correct-horse-123")
    project = await ProjectService(db_session).create(owner.id, "Not Yours")
    await _login(db_session, auth_client, "patch-stranger@example.com")

    response = await auth_client.patch(
        f"/api/v1/projects/{project.id}", json={"title": "Hijacked"}
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/projects/{project_id} (T050)
# ---------------------------------------------------------------------------


async def test_delete_project_moves_to_trash(auth_client, db_session):
    user = await _login(db_session, auth_client, "delete-ok@example.com")
    project = await ProjectService(db_session).create(user.id, "Deletable Project")

    response = await auth_client.delete(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["deletion_status"] == "trashed"
    assert body["trashed_at"] is not None
    assert body["scheduled_deletion_at"] is not None


async def test_delete_project_rejects_missing_auth(auth_client, db_session):
    user = await UserService(db_session).register(
        "delete-noauth@example.com", "correct-horse-123"
    )
    project = await ProjectService(db_session).create(user.id, "No Auth Project")

    response = await auth_client.delete(f"/api/v1/projects/{project.id}")

    assert response.status_code == 401


async def test_delete_project_404_for_another_users_project(auth_client, db_session):
    owner = await UserService(db_session).register(
        "delete-owner@example.com", "correct-horse-123"
    )
    project = await ProjectService(db_session).create(owner.id, "Not Yours")
    await _login(db_session, auth_client, "delete-stranger@example.com")

    response = await auth_client.delete(f"/api/v1/projects/{project.id}")

    assert response.status_code == 404
