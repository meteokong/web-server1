"""Integration tests for the get_current_user auth dependency — run
against the real database and a real FastAPI app so the full chain
(cookie -> dependency -> TokenService -> DB user lookup) is actually
exercised, not mocked.

Uses httpx.AsyncClient over ASGITransport rather than
fastapi.testclient.TestClient: TestClient drives the ASGI app from a
separate thread with its own event loop, which asyncpg's connections
(tied to the loop that created them) don't tolerate — queries made
during the request would intermittently fail or corrupt teardown with
"Event loop is closed" / "attached to a different loop" errors.
ASGITransport instead calls the app in-process, on this same test's
event loop, so the DB session fixture's connection is always used from
the one loop that created it.
"""

import uuid

import httpx
from fastapi import Depends, FastAPI

from src.api.dependencies import ACCESS_TOKEN_COOKIE_NAME, get_current_user
from src.api.exceptions import register_exception_handlers
from src.db.session import get_db
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService
from src.utils.jwt import create_access_token


def _build_test_app(db_session) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[get_db] = lambda: db_session

    @app.get("/whoami")
    async def whoami(current_user=Depends(get_current_user)):
        return {"id": str(current_user.id), "email": current_user.email}

    return app


def _client_for(db_session) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=_build_test_app(db_session))
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


async def test_valid_access_token_cookie_resolves_the_user(db_session):
    user = await UserService(db_session).register("dep-ok@example.com", "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)

    async with _client_for(db_session) as client:
        client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.access_token)
        response = await client.get("/whoami")

    assert response.status_code == 200
    assert response.json() == {"id": str(user.id), "email": "dep-ok@example.com"}


async def test_missing_cookie_is_rejected(db_session):
    async with _client_for(db_session) as client:
        response = await client.get("/whoami")
    assert response.status_code == 401


async def test_garbage_cookie_is_rejected(db_session):
    async with _client_for(db_session) as client:
        client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, "not-a-real-token")
        response = await client.get("/whoami")
    assert response.status_code == 401


async def test_refresh_token_used_as_access_cookie_is_rejected(db_session):
    """Type confusion: a refresh token must not work as an access token here either."""
    user = await UserService(db_session).register("dep-wrong-type@example.com", "correct-horse-123")
    pair = await TokenService(db_session).issue_tokens(user)

    async with _client_for(db_session) as client:
        client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, pair.refresh_token)
        response = await client.get("/whoami")

    assert response.status_code == 401


async def test_well_signed_token_for_deleted_user_is_rejected(db_session):
    """A structurally valid access token whose user no longer exists in
    the DB must not resolve to a phantom user."""
    phantom_token = create_access_token(str(uuid.uuid4()))

    async with _client_for(db_session) as client:
        client.cookies.set(ACCESS_TOKEN_COOKIE_NAME, phantom_token)
        response = await client.get("/whoami")

    assert response.status_code == 401
