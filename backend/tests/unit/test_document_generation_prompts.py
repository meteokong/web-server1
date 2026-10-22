"""Unit tests for the 7-chapter document-generation prompt templates (T092).

These only assert on the generated prompt STRINGS (no Gemini calls) —
that the required structure/rules from spec.md's FR-026..FR-039 and
data-model.md's `content` JSON shape are present in what gets sent to the
model.
"""

import pytest

from src.services.ai.prompts import (
    SYSTEM_INSTRUCTION,
    CodeFileInput,
    build_document_generation_prompt,
)


def test_system_instruction_targets_complete_beginners():
    assert "beginner" in SYSTEM_INSTRUCTION.lower()
    assert "zero programming knowledge" in SYSTEM_INSTRUCTION.lower()


def test_raises_on_empty_file_list():
    with pytest.raises(ValueError):
        build_document_generation_prompt(files=[])


def test_prompt_includes_file_name_and_content():
    files = [CodeFileInput(file_name="main.py", content="def add(a, b):\n    return a + b")]

    prompt = build_document_generation_prompt(files=files)

    assert "main.py" in prompt
    assert "def add(a, b):" in prompt


def test_prompt_includes_multiple_files():
    files = [
        CodeFileInput(file_name="main.py", content="import utils"),
        CodeFileInput(file_name="utils.py", content="def helper(): pass"),
    ]

    prompt = build_document_generation_prompt(files=files)

    assert "main.py" in prompt
    assert "utils.py" in prompt
    assert "import utils" in prompt
    assert "def helper(): pass" in prompt


def test_prompt_includes_language_and_complexity_when_given():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(
        files=files, language="python", complexity_level="beginner"
    )

    assert "python" in prompt.lower()
    assert "beginner" in prompt.lower()


def test_prompt_omits_language_and_complexity_when_not_given():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(files=files)

    assert "Detected language" not in prompt
    assert "Complexity level" not in prompt


def test_prompt_mentions_all_seven_chapter_keys():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(files=files)

    for i in range(1, 8):
        assert f"chapter{i}" in prompt


def test_prompt_enforces_chapter2_concept_card_limit():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(files=files)

    assert "5 concept" in prompt


def test_prompt_enforces_chapter7_mistake_count_range():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(files=files)

    assert "3 and 5" in prompt or "3-5" in prompt


def test_prompt_requires_json_only_output():
    files = [CodeFileInput(file_name="main.py", content="x = 1")]

    prompt = build_document_generation_prompt(files=files)

    assert "JSON" in prompt
    assert "no markdown" in prompt.lower() or "ONLY the JSON" in prompt
