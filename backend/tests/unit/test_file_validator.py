"""Unit tests for file validation utilities (T064).

Allowed extensions and the 10MB size limit mirror the `supported_extension`
and `valid_upload_size` CHECK constraints on the `code_files`/`uploaded_code`
tables (T009 migration) — see data-model.md.
"""

import pytest

from src.api.exceptions import ValidationAppError
from src.utils.file_validator import (
    MAX_FILE_SIZE_BYTES,
    is_binary,
    validate_extension,
    validate_not_binary,
    validate_size,
)


@pytest.mark.parametrize(
    "filename",
    [
        "main.py",
        "App.jsx",
        "utils.JS",  # case-insensitive
        "index.html",
        "styles.css",
        "Main.java",
        "a.cpp",
        "a.c",
        "notes.txt",
        "README.md",
    ],
)
def test_validate_extension_accepts_whitelisted_extensions(filename):
    assert validate_extension(filename) == "." + filename.rsplit(".", 1)[1].lower()


@pytest.mark.parametrize("filename", ["image.png", "archive.zip", "binary.exe", "no_extension"])
def test_validate_extension_rejects_everything_else(filename):
    with pytest.raises(ValidationAppError):
        validate_extension(filename)


def test_validate_size_accepts_up_to_the_limit():
    validate_size(MAX_FILE_SIZE_BYTES)  # exactly at the limit — must not raise


def test_validate_size_rejects_over_the_limit():
    with pytest.raises(ValidationAppError):
        validate_size(MAX_FILE_SIZE_BYTES + 1)


def test_is_binary_true_for_content_with_a_null_byte():
    assert is_binary(b"\x00\x01\x02binarystuff") is True


def test_is_binary_false_for_plain_text():
    assert is_binary("def hello():\n    print('hi')\n".encode("utf-8")) is False


def test_is_binary_false_for_empty_content():
    assert is_binary(b"") is False


def test_validate_not_binary_raises_for_binary_content():
    with pytest.raises(ValidationAppError):
        validate_not_binary(b"\x00\x01\x02")


def test_validate_not_binary_accepts_text_content():
    validate_not_binary(b"print('hello world')")  # must not raise
