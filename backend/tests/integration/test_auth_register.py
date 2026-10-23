"""Integration tests for POST /api/v1/auth/register (T028).

See tests/integration/conftest.py for the ``auth_client`` fixture
(real app, httpx.AsyncClient + ASGITransport, real DB session).
"""

from src.services.auth.user_service import UserService


async def test_register_creates_user_and_returns_201(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "register-api-ok@example.com", "password": "correct-horse-123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "register-api-ok@example.com"
    assert "id" in body
    assert "skill_level" in body
    assert "created_at" in body
    assert "password" not in body
    assert "password_hash" not in body

    # Register never logs the user in — no cookies set.
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


async def test_register_rejects_duplicate_email(auth_client, db_session):
    await UserService(db_session).register("register-api-dup@example.com", "correct-horse-123")

    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "register-api-dup@example.com", "password": "another-pass-1"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "conflict"


async def test_register_rejects_weak_password(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "register-api-weak@example.com", "password": "short1"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "validation_error"
