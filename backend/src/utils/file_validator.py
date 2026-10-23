"""File validation utilities for code uploads (T064): extension whitelist,
size limit, and binary-content detection.

Mirrors the `supported_extension` and `valid_upload_size` CHECK constraints
on the `code_files`/`uploaded_code` tables (T009 migration) — these are the
application-level checks that run before a row would ever violate them, so
a bad upload gets a clear 400 instead of a raw IntegrityError.
"""

from pathlib import Path

from src.api.exceptions import ValidationAppError

# Must match the `supported_extension` CHECK constraint on code_files
# (backend/alembic/versions/001_initial_schema.py) exactly.
ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".java",
    ".cpp",
    ".c",
    ".txt",
    ".md",
}

# Must match the `valid_upload_size` CHECK constraint on uploaded_code
# (upload_size_bytes <= 10485760) and .env.example's MAX_UPLOAD_SIZE_MB=10.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# spec.md edge case: "Maximum 20 files per upload. Please select fewer
# files or use folder upload."
MAX_FILES_PER_UPLOAD = 20

# A null byte anywhere in the content is a reliable, cheap signal that it's
# not text — real source files in the allowed extensions never contain one.
_BINARY_MARKER = b"\x00"


def validate_extension(filename: str) -> str:
    """Return the (lowercased) extension if it's on the whitelist.
    Raises ValidationAppError otherwise."""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationAppError(f"unsupported file extension: {extension or '(none)'}")
    return extension


def validate_size(size_bytes: int) -> None:
    """Raise ValidationAppError if `size_bytes` exceeds the 10MB limit."""
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValidationAppError(f"file exceeds the {MAX_FILE_SIZE_BYTES}-byte size limit")


def is_binary(content: bytes) -> bool:
    """Heuristic binary-content check: a null byte anywhere in `content`
    means it isn't text."""
    return _BINARY_MARKER in content


def validate_not_binary(content: bytes) -> None:
    """Raise ValidationAppError if `content` looks like a binary file."""
    if is_binary(content):
        raise ValidationAppError("binary files are not supported")


def validate_file_count(count: int) -> None:
    """Raise ValidationAppError if `count` exceeds the per-upload file limit."""
    if count > MAX_FILES_PER_UPLOAD:
        raise ValidationAppError(
            f"Maximum {MAX_FILES_PER_UPLOAD} files per upload. "
            "Please select fewer files or use folder upload."
        )
