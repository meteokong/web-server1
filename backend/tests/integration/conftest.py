"""Shared fixtures for auth API integration tests (T028-T031).

``auth_client`` drives the real FastAPI app (``src.main.app``) through
``httpx.AsyncClient`` + ``httpx.ASGITransport`` (see test_dependencies.py /
docs/task-reports/TASK-027-*.md for why TestClient is unsafe here), with
``get_db`` overridden to the test's own ``db_session`` fixture so every
auth route exercises the real DB-fixture-backed session rather than the
app's own engine/pool.
"""

import httpx
import pytest

from src.db.session import get_db
from src.main import app


@pytest.fixture
async def auth_client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.pop(get_db, None)
