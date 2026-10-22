"""Unit tests for the language detection service (T065).

Extension-to-language mapping mirrors file_validator.ALLOWED_EXTENSIONS —
every file reaching this service already passed extension validation, so
the Pygments content fallback only matters for extensionless files.
"""

import pytest

from src.services.code_analysis.language_detector import (
    UNKNOWN_LANGUAGE,
    detect_file_language,
    detect_project_language,
)


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("main.py", "python"),
        ("app.js", "javascript"),
        ("App.jsx", "javascript"),
        ("index.ts", "typescript"),
        ("Component.tsx", "typescript"),
        ("Main.java", "java"),
        ("a.cpp", "cpp"),
        ("a.c", "c"),
        ("index.html", "html"),
        ("styles.css", "css"),
        ("notes.txt", "text"),
        ("README.md", "markdown"),
    ],
)
def test_detect_file_language_by_extension(filename, expected):
    assert detect_file_language(filename) == expected


def test_detect_file_language_extension_is_case_insensitive():
    assert detect_file_language("Main.PY") == "python"


def test_detect_file_language_falls_back_to_pygments_for_shebang_python():
    content = "#!/usr/bin/env python\nimport os\n\nprint('hi')\n"
    assert detect_file_language("script", content) == "python"


def test_detect_file_language_falls_back_to_pygments_for_html_doctype():
    content = "<!DOCTYPE html>\n<html><body><p>Hello</p></body></html>\n"
    assert detect_file_language("noext", content) == "html"


def test_detect_file_language_returns_unknown_for_unrecognizable_content():
    assert detect_file_language("noext", "just some plain ambiguous words") == UNKNOWN_LANGUAGE


def test_detect_file_language_returns_unknown_for_empty_content_and_no_extension():
    assert detect_file_language("noext", "") == UNKNOWN_LANGUAGE


def test_detect_file_language_decodes_bytes_content():
    content = b"#!/usr/bin/env python\nprint('hi')\n"
    assert detect_file_language("script", content) == "python"


def test_detect_project_language_returns_dominant_language():
    filenames = ["a.py", "b.py", "c.py", "d.js"]
    assert detect_project_language(filenames) == "python"


def test_detect_project_language_ignores_unknown_files():
    filenames = ["noext1", "noext2", "a.py"]
    assert detect_project_language(filenames) == "python"


def test_detect_project_language_returns_unknown_for_empty_list():
    assert detect_project_language([]) == UNKNOWN_LANGUAGE


def test_detect_project_language_returns_unknown_when_all_unrecognized():
    assert detect_project_language(["noext1", "noext2"]) == UNKNOWN_LANGUAGE
