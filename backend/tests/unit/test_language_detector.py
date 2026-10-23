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


def test_detect_file_language_falls_back_to_keywords_for_javascript():
    # JavascriptLexer has no custom analyse_text (always scores 0.0), so
    # this must be resolved by the keyword-marker fallback, not Pygments.
    content = (
        "class Item {\n"
        "  constructor(name, qty) {\n"
        "    this.name = name;\n"
        "    this.qty = qty;\n"
        "  }\n"
        "}\n"
        "const inv = new Item('widget', 10);\n"
        "console.log(`Total: ${inv.qty}`);\n"
        "module.exports = Item;\n"
    )
    assert detect_file_language("noext", content) == "javascript"


def test_detect_file_language_falls_back_to_keywords_for_typescript():
    content = (
        "interface Item {\n"
        "  name: string;\n"
        "  quantity: number;\n"
        "}\n"
        "export type ItemList = Item[];\n"
        "function total(items: ItemList): number {\n"
        "  return items.reduce((sum, i) => sum + i.quantity, 0);\n"
        "}\n"
    )
    assert detect_file_language("noext", content) == "typescript"


def test_detect_file_language_falls_back_to_keywords_for_java():
    content = (
        "import java.util.List;\n\n"
        "public class Hello {\n"
        "    public static void main(String[] args) {\n"
        '        System.out.println("Hello");\n'
        "    }\n"
        "}\n"
    )
    assert detect_file_language("noext", content) == "java"


def test_detect_file_language_falls_back_to_keywords_for_css():
    content = (
        "@media (max-width: 600px) {\n"
        "  .container {\n"
        "    color: red;\n"
        "    margin: 0 auto;\n"
        "  }\n"
        "}\n"
    )
    assert detect_file_language("noext", content) == "css"


def test_detect_file_language_returns_unknown_for_unrecognizable_content():
    assert detect_file_language("noext", "just some plain ambiguous words") == UNKNOWN_LANGUAGE


def test_detect_file_language_returns_unknown_for_empty_content_and_no_extension():
    assert detect_file_language("noext", "") == UNKNOWN_LANGUAGE


def test_detect_file_language_decodes_bytes_content():
    content = b"#!/usr/bin/env python\nprint('hi')\n"
    assert detect_file_language("script", content) == "python"


def test_detect_file_language_returns_unknown_for_undecodable_bytes():
    content = b"\xff\xfe\x00\x01not valid utf-8"
    assert detect_file_language("noext", content) == UNKNOWN_LANGUAGE


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
