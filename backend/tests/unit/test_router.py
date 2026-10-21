import importlib

from fastapi import APIRouter
from fastapi.testclient import TestClient

from src.api.router import api_router


def test_api_router_has_v1_prefix():
    assert isinstance(api_router, APIRouter)
    assert api_router.prefix == "/api/v1"


def test_app_mounts_api_router_at_v1_prefix():
    """Prove src/main.py actually wires api_router in, not just that the
    router object itself has the right prefix (the two can drift apart:
    e.g. a typo'd prefix or a forgotten include_router() call)."""
    import src.main as main_module

    # Register a throwaway route on the real router singleton, then reload
    # main so it re-runs app.include_router(api_router) and picks it up.
    @api_router.get("/_router_wiring_smoke_test")
    def _smoke() -> dict[str, bool]:
        return {"ok": True}

    try:
        importlib.reload(main_module)
        client = TestClient(main_module.app)
        response = client.get("/api/v1/_router_wiring_smoke_test")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    finally:
        # Clean up: drop the throwaway route and restore main's app.
        api_router.routes.pop()
        importlib.reload(main_module)
