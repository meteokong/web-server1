"""Integration tests for GET /api/v1/auth/me (T029A).

See tests/integration/conftest.py for the ``auth_client`` fixture
(real app, httpx.AsyncClient + ASGITransport, real DB session).
"""

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService


async def test_me_returns_current_user_for_valid_cookie(auth_client, db_session):
    user = await UserService(db_session).register("me-api-ok@example.com", "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)

    auth_client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.access_token)
    response = await auth_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == "me-api-ok@example.com"
    assert "password" not in body
    assert "password_hash" not in body


async def test_me_rejects_missing_cookie(auth_client):
    response = await auth_client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


async def test_me_rejects_garbage_cookie(auth_client):
    auth_client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, "not-a-real-token")
    response = await auth_client.get("/api/v1/auth/me")

    assert response.status_code == 401


async def test_me_rejects_refresh_token_used_as_access_cookie(auth_client, db_session):
    user = await UserService(db_session).register(
        "me-api-wrong-type@example.com", "correct-horse-123"
    )
    pair = await TokenService(db_session).issue_tokens(user)

    auth_client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.refresh_token)
    response = await auth_client.get("/api/v1/auth/me")

    assert response.status_code == 401
