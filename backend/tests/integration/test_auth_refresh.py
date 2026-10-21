"""Integration tests for POST /api/v1/auth/refresh (T031).

See tests/integration/conftest.py for the ``auth_client`` fixture
(real app, httpx.AsyncClient + ASGITransport, real DB session).
"""

from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService

REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


async def test_refresh_rotates_cookies_and_returns_current_user(auth_client, db_session):
    user = await UserService(db_session).register(
        "refresh-api-ok@example.com", "correct-horse-123"
    )
    pair = await TokenService(db_session).issue_tokens(user)

    auth_client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, pair.refresh_token)
    response = await auth_client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == "refresh-api-ok@example.com"

    new_access = response.cookies.get("access_token")
    new_refresh = response.cookies.get("refresh_token")
    assert new_access is not None
    assert new_refresh is not None
    assert new_access != pair.access_token
    assert new_refresh != pair.refresh_token


async def test_refresh_rejects_missing_cookie(auth_client):
    response = await auth_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


async def test_refresh_rejects_garbage_cookie_and_clears_cookies(auth_client):
    auth_client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "not-a-real-token")
    response = await auth_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    set_cookie_headers = response.headers.get_list("set-cookie")
    access_clear = next(h for h in set_cookie_headers if h.startswith("access_token="))
    refresh_clear = next(h for h in set_cookie_headers if h.startswith("refresh_token="))
    assert "Max-Age=0" in access_clear
    assert "Max-Age=0" in refresh_clear


async def test_refresh_rejects_reuse_of_an_already_rotated_token(auth_client, db_session):
    user = await UserService(db_session).register(
        "refresh-api-reuse@example.com", "correct-horse-123"
    )
    pair = await TokenService(db_session).issue_tokens(user)

    auth_client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, pair.refresh_token)
    first_response = await auth_client.post("/api/v1/auth/refresh")
    assert first_response.status_code == 200

    # Re-send the now-stale original refresh token.
    auth_client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, pair.refresh_token)
    second_response = await auth_client.post("/api/v1/auth/refresh")

    assert second_response.status_code == 401
