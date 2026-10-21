"""Integration tests for POST /api/v1/auth/login (T029).

See tests/integration/conftest.py for the ``auth_client`` fixture
(real app, httpx.AsyncClient + ASGITransport, real DB session).
"""

from src.services.auth.user_service import UserService


async def _register(db_session, email="login-api-ok@example.com", password="correct-horse-123"):
    return await UserService(db_session).register(email, password)


async def test_login_succeeds_and_sets_cookies(auth_client, db_session):
    await _register(db_session)

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login-api-ok@example.com", "password": "correct-horse-123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "login-api-ok@example.com"
    assert "password" not in body
    assert "password_hash" not in body

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    set_cookie_headers = response.headers.get_list("set-cookie")
    access_cookie_header = next(h for h in set_cookie_headers if h.startswith("access_token="))
    assert "HttpOnly" in access_cookie_header
    assert "SameSite=strict" in access_cookie_header


async def test_login_rejects_wrong_password(auth_client, db_session):
    await _register(db_session, email="login-api-wrongpw@example.com")

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login-api-wrongpw@example.com", "password": "totally-wrong-1"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "unauthorized"
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


async def test_login_rejects_unknown_email_with_same_error_as_wrong_password(
    auth_client, db_session
):
    await _register(db_session, email="login-api-enum@example.com")

    unknown_response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login-api-does-not-exist@example.com", "password": "whatever-123"},
    )
    wrong_pw_response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login-api-enum@example.com", "password": "wrong-password-1"},
    )

    assert unknown_response.status_code == 401
    assert wrong_pw_response.status_code == 401
    assert (
        unknown_response.json()["error"]["message"] == wrong_pw_response.json()["error"]["message"]
    )
