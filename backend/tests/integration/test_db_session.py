"""Regression test for src/db/session.py's get_db dependency.

Every other integration test overrides `get_db` with the test's own
`db_session` fixture (see tests/integration/conftest.py's auth_client),
which is correct for isolating tests from each other — but it also means
no test ever exercised the REAL get_db that the running dev/prod server
actually uses. This test deliberately does NOT override get_db: it drives
the real app with the real dependency, then opens a brand new, independent
engine/session (not the app's own pool) to check whether the write
actually landed in the database — i.e. whether get_db's session was ever
committed.
"""

import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.config import get_database_settings
from src.main import app
from src.models.user import User


async def test_register_through_the_real_app_actually_persists_the_user():
    email = f"db-session-regression-{uuid.uuid4().hex[:8]}@example.com"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/register", json={"email": email, "password": "correct-horse-123"}
        )
    assert response.status_code == 201

    # Independent connection — not the app's engine/pool, not a test
    # fixture session — so this only sees what was actually committed.
    settings = get_database_settings()
    engine = create_async_engine(settings.async_database_url)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    try:
        async with session_factory() as verify_session:
            persisted = await verify_session.scalar(select(User).where(User.email == email))
            assert persisted is not None, (
                "register() returned 201 but the row was never committed — "
                "get_db() must commit the session after a successful request"
            )
    finally:
        await engine.dispose()
