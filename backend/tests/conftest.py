"""Shared pytest fixtures for tests that need a real database session."""

import pytest

from src.db.session import AsyncSessionLocal


@pytest.fixture
async def db_session():
    """A real AsyncSession against the live DB (see docker-compose.yml).

    Nothing a test does through this session is ever committed — only
    flushed (so uniqueness/FK checks still run for real) — and the
    session is rolled back on teardown, so tests never leave data behind.
    """
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
