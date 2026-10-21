"""Database configuration (connection URL + pool sizing), read from the
environment / project-root ``.env`` (see ``.env.example``).

This is the single source of truth for DB connection settings; ``session.py``
builds its engine from here instead of reading ``os.environ`` directly.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is three levels up from backend/src/db/config.py
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class DatabaseSettings(BaseSettings):
    """DATABASE_URL plus SQLAlchemy connection-pool tuning, all overridable via env vars."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/codelearning"

    # Pool sizing: default supports the "3 concurrent document generations
    # per user" + normal API traffic target from plan.md without exhausting
    # PostgreSQL's default max_connections (100).
    db_pool_size: int = 10
    db_max_overflow: int = 5
    db_pool_timeout: int = 30
    db_pool_recycle_seconds: int = 1800  # recycle connections every 30 min

    @property
    def async_database_url(self) -> str:
        """DATABASE_URL converted to the asyncpg driver scheme the async engine needs."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
