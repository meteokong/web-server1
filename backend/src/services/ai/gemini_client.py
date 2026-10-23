"""Gemini API client wrapper (T091).

A thin wrapper around `google.genai.Client` that resolves configuration
(GOOGLE_API_KEY, model name) from the environment / .env and exposes a
single `generate_content` call point for the rest of the app — document
generation (T093+), Q&A, etc. — so callers never touch the SDK directly.

Retry/backoff policy is intentionally NOT handled here: different callers
need different policies (e.g. document generation's "up to 3 retries" per
research.md vs. a Q&A request that should fail fast), so that logic lives
in the caller (see DocumentGenerationService, T093) using the
GeminiAPIError this wrapper raises.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_ENV_FILE = _PROJECT_ROOT / ".env"


class GeminiSettings(BaseSettings):
    """GOOGLE_API_KEY and model name, read from the environment / .env."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    google_api_key: str = ""
    # research.md: "Same model for both document generation and Q&A
    # (unified, cost-effective)".
    gemini_model: str = "gemini-3-flash-preview"


@lru_cache
def get_gemini_settings() -> GeminiSettings:
    return GeminiSettings()


class GeminiClientError(Exception):
    """Base class for errors raised by GeminiClient."""


class GeminiConfigError(GeminiClientError):
    """Raised when required configuration (e.g. GOOGLE_API_KEY) is missing."""


class GeminiAPIError(GeminiClientError):
    """Raised when the Gemini API itself returns an error (wraps the SDK's
    google.genai.errors.APIError so callers don't need to import the SDK)."""

    def __init__(self, message: str, *, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


class GeminiClient:
    """Wraps a single `google.genai.Client` + model pair."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        settings = get_gemini_settings()
        self._model = model or settings.gemini_model

        if client is not None:
            self._client = client
            return

        resolved_key = api_key if api_key is not None else settings.google_api_key
        if not resolved_key:
            raise GeminiConfigError(
                "GOOGLE_API_KEY is not set (checked constructor arg, then .env)"
            )
        self._client = genai.Client(api_key=resolved_key)

    def generate_content(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        """Send `prompt` to the configured model and return the response text.

        `response_mime_type="application/json"` enables Gemini's native
        JSON mode (used by document generation, T092/T093, for the
        7-chapter structured output).
        """
        config = None
        if system_instruction is not None or response_mime_type is not None:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
            )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
        except genai_errors.APIError as exc:
            raise GeminiAPIError(str(exc), code=exc.code) from exc

        return response.text
