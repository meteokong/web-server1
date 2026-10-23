"""Application-wide settings (environment, debug flag, CORS), read from
the environment / project-root ``.env`` (see ``.env.example``).
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        """ALLOWED_ORIGINS ("a,b,c") split into a list, ignoring blanks/whitespace."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


class StorageSettings(BaseSettings):
    """UPLOAD_DIR: where uploaded code files are written (see file_storage.py, T067)."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    upload_dir: str = "./storage/uploads"

    @property
    def upload_root(self) -> Path:
        """``upload_dir`` resolved to an absolute path, relative to the
        project root (matching .env.example's `./storage/uploads`)."""
        root = Path(self.upload_dir)
        return root if root.is_absolute() else _PROJECT_ROOT / root


@lru_cache
def get_storage_settings() -> StorageSettings:
    return StorageSettings()
