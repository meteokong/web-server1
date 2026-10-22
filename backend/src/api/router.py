"""Top-level API router, mounted at ``/api/v1`` in ``src/main.py``.

Each feature area (auth, projects, tasks, documents, practice, qa,
progress, trash) defines its own ``APIRouter`` in its own module and gets
included here as it's built out, e.g.:

    from src.api.auth import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

Keeping that registration in one place means ``src/main.py`` never needs
to know about individual feature routers.
"""

from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.documents import router as documents_router
from src.api.projects import router as projects_router
from src.api.tasks import router as tasks_router
from src.config import get_app_settings

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
# No fixed prefix: tasks.py's routes mix /projects/{project_id}/tasks and
# /tasks/{task_id} path shapes and spell out their own full paths.
api_router.include_router(tasks_router, tags=["tasks"])
# Same reasoning as tasks_router: every route already spells out its own
# full /tasks/{task_id}/document... path.
api_router.include_router(documents_router, tags=["documents"])


@api_router.get("/health")
async def health_check_v1() -> dict[str, str]:
    """Versioned counterpart to the root /health (src/main.py) — lets the
    frontend health-check the API through the same /api/v1 base URL it
    uses for everything else."""
    settings = get_app_settings()
    return {"status": "ok", "environment": settings.environment}
