"""FastAPI application entry point: app instance + CORS + global error handling.

Feature routers (auth, projects, tasks, ...) are registered onto
``api_router`` in ``src/api/router.py`` (T015) and mounted here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exceptions import register_exception_handlers
from src.api.router import api_router
from src.config import get_app_settings

settings = get_app_settings()

app = FastAPI(
    title="AI Code Learning Platform API",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness check: confirms the app booted and is serving requests."""
    return {"status": "ok", "environment": settings.environment}
