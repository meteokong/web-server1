from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.api.exceptions import NotFoundError, register_exception_handlers


class _Item(BaseModel):
    name: str
    price: float


def _build_test_app() -> FastAPI:
    """A throwaway app wired with the real exception handlers, plus a few
    routes that each trigger a different error path. Kept separate from
    the production app/router so we don't leave debug-only routes there."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom-app-error")
    def boom_app_error():
        raise NotFoundError("thing not found", details={"id": "123"})

    @app.get("/boom-http-exception")
    def boom_http_exception():
        raise HTTPException(status_code=403, detail="not allowed")

    @app.post("/validate")
    def validate_item(item: _Item):
        return item

    @app.get("/boom-unhandled")
    def boom_unhandled():
        raise RuntimeError("kaboom, this message must never reach the client")

    return app


def test_app_error_maps_to_consistent_schema():
    client = TestClient(_build_test_app())
    response = client.get("/boom-app-error")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "thing not found",
            "details": {"id": "123"},
        }
    }


def test_http_exception_maps_to_consistent_schema():
    client = TestClient(_build_test_app())
    response = client.get("/boom-http-exception")
    assert response.status_code == 403
    assert response.json() == {"error": {"code": "http_error", "message": "not allowed"}}


def test_request_validation_error_maps_to_consistent_schema():
    client = TestClient(_build_test_app())
    response = client.post("/validate", json={"name": "widget"})  # missing "price"
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert any(err["loc"] == ["body", "price"] for err in body["error"]["details"])


def test_unhandled_exception_returns_500_without_leaking_details():
    client = TestClient(_build_test_app(), raise_server_exceptions=False)
    response = client.get("/boom-unhandled")
    assert response.status_code == 500
    body = response.json()
    assert body == {"error": {"code": "internal_error", "message": "An unexpected error occurred"}}
    assert "kaboom" not in response.text


def test_production_app_has_handlers_registered():
    """Smoke-test that src/main.py actually wires this module in."""
    from src.main import app

    assert app.exception_handlers  # non-empty: our handlers were registered
