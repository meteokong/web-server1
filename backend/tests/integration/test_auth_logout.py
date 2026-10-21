"""Integration tests for POST /api/v1/auth/logout (T030).

See tests/integration/conftest.py for the ``auth_client`` fixture
(real app, httpx.AsyncClient + ASGITransport, real DB session).
"""

from sqlalchemy import select

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME
from src.models.refresh_token import RefreshToken
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService


async def test_logout_revokes_all_refresh_tokens_and_clears_cookies(auth_client, db_session):
    user = await UserService(db_session).register("logout-api-ok@example.com", "correct-horse-123")
    token_service = TokenService(db_session)
    pair1 = await token_service.issue_tokens(user)
    await token_service.issue_tokens(user)  # a second session for the same user

    auth_client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair1.access_token)
    response = await auth_client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "logged out"}

    # delete_cookie() clears a cookie by re-setting it with Max-Age=0.
    set_cookie_headers = response.headers.get_list("set-cookie")
    access_clear = next(h for h in set_cookie_headers if h.startswith("access_token="))
    refresh_clear = next(h for h in set_cookie_headers if h.startswith("refresh_token="))
    assert "Max-Age=0" in access_clear
    assert "Max-Age=0" in refresh_clear

    result = await db_session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    rows = result.scalars().all()
    assert len(rows) == 2
    assert all(row.revoked is True for row in rows)


async def test_logout_rejects_missing_cookie(auth_client):
    response = await auth_client.post("/api/v1/auth/logout")

    assert response.status_code == 401
