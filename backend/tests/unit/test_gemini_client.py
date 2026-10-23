"""Unit tests for the Gemini API client wrapper (T091).

No network calls are made: the underlying `google.genai.Client` is replaced
with a fake object so these tests only exercise GeminiClient's own wiring
(config resolution, request building, response/error translation).
"""

import pytest
import requests
from google.genai import errors as genai_errors

from src.services.ai.gemini_client import (
    GeminiAPIError,
    GeminiClient,
    GeminiConfigError,
)


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeModels:
    def __init__(self, response=None, exception=None) -> None:
        self._response = response
        self._exception = exception
        self.calls: list[dict] = []

    def generate_content(self, *, model, contents, config=None):
        self.calls.append({"model": model, "contents": contents, "config": config})
        if self._exception is not None:
            raise self._exception
        return self._response


class _FakeGenaiClient:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models


def test_missing_api_key_raises_config_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    from src.services.ai import gemini_client as module

    module.get_gemini_settings.cache_clear()
    with pytest.raises(GeminiConfigError):
        GeminiClient(api_key="")


def test_generate_content_returns_response_text():
    fake_models = _FakeModels(response=_FakeResponse("hello world"))
    client = GeminiClient(client=_FakeGenaiClient(fake_models))

    result = client.generate_content("explain this code")

    assert result == "hello world"
    assert fake_models.calls[0]["contents"] == "explain this code"


def test_generate_content_uses_configured_model_name():
    fake_models = _FakeModels(response=_FakeResponse("ok"))
    client = GeminiClient(client=_FakeGenaiClient(fake_models), model="gemini-3-flash-preview")

    client.generate_content("hi")

    assert fake_models.calls[0]["model"] == "gemini-3-flash-preview"


def test_generate_content_passes_system_instruction_and_json_mode():
    fake_models = _FakeModels(response=_FakeResponse("{}"))
    client = GeminiClient(client=_FakeGenaiClient(fake_models))

    client.generate_content(
        "generate the document",
        system_instruction="You are an expert teacher.",
        response_mime_type="application/json",
    )

    config = fake_models.calls[0]["config"]
    assert config.system_instruction == "You are an expert teacher."
    assert config.response_mime_type == "application/json"


def test_generate_content_wraps_api_errors():
    fake_response = requests.Response()
    fake_response.status_code = 429
    fake_response._content = (
        b'{"error": {"message": "quota exceeded", "status": "RESOURCE_EXHAUSTED"}}'
    )
    api_error = genai_errors.APIError(429, fake_response)
    fake_models = _FakeModels(exception=api_error)
    client = GeminiClient(client=_FakeGenaiClient(fake_models))

    with pytest.raises(GeminiAPIError) as exc_info:
        client.generate_content("hi")

    assert exc_info.value.code == 429
