"""Shared pytest fixtures for tests that need a real database session."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.config import get_database_settings


@pytest.fixture
async def db_session():
    """A real AsyncSession against the live DB (see docker-compose.yml).

    Builds its own engine (rather than reusing the module-level singleton
    from src/db/session.py) bound to *this test's* event loop — asyncpg
    connections are tied to the loop that created them, and pytest-asyncio
    gives each test function its own loop, so sharing one engine/pool
    across tests intermittently raises "Event loop is closed" errors.

    Note for tests that also drive a FastAPI app through this session
    (e.g. tests/integration/test_dependencies.py): use httpx.AsyncClient
    with httpx.ASGITransport, not fastapi.testclient.TestClient.
    TestClient runs the app on a separate thread with its own event
    loop, which breaks this same-loop assumption; ASGITransport calls
    the app in-process on the current loop.

    Nothing a test does through this session is ever committed — only
    flushed (so uniqueness/FK checks still run for real) — and the
    engine is disposed on teardown, so tests never leave data behind.
    """
    settings = get_database_settings()
    engine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()
