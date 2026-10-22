"""Celery application: Redis as both message broker and result backend.

Individual background tasks (document generation, practice generation,
trash cleanup, ...) will be defined in their own modules under
``src/tasks/`` (e.g. ``src/tasks/document_generation.py``), each importing
``celery_app`` from here and decorating its function with
``@celery_app.task``. Celery only registers a task once its module has
been imported, so as those modules are added, list them in ``include``
below (or make sure whatever starts the worker imports them) — Celery's
``autodiscover_tasks`` doesn't apply here since it looks for a nested
``<package>.tasks`` submodule, which isn't this project's layout (task
modules live directly inside the ``tasks`` package itself).
"""

from functools import lru_cache
from pathlib import Path

from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class CelerySettings(BaseSettings):
    """REDIS_URL, read from the environment / project-root .env (see .env.example)."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    redis_url: str = "redis://localhost:6379/0"


@lru_cache
def get_celery_settings() -> CelerySettings:
    return CelerySettings()


_settings = get_celery_settings()

celery_app = Celery(
    "code_study",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
    include=[
        "src.tasks.document_generation",  # T094
        # "src.tasks.practice_generation",  # T118
        # "src.tasks.trash_cleanup",        # T172
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Surface "started" state so long AI-generation tasks (T094/T118) can
    # report progress instead of looking stuck at "pending".
    task_track_started=True,
    # Document generation can take up to the plan.md 3-minute target;
    # give the worker headroom before Celery force-kills the task.
    task_time_limit=5 * 60,
)
