"""File storage service (T067): persist one uploaded code file's content to
disk under ``storage/uploads/{user_id}/{task_id}/{relative_path}``.

Security: ``relative_path`` comes straight from user-controlled multipart
upload input (filenames, folder-relative paths). This module rejects any
path that is blank, absolute (POSIX ``/...`` or a Windows drive like
``C:\\...``), or escapes the task's own directory via ``..`` segments,
by inspecting the path's parts before it's ever joined onto a real
filesystem path — a relative path with no ``..`` segments and no
absolute root can only resolve to somewhere under the task directory.
"""

import re
import uuid
from pathlib import Path, PurePosixPath

from src.api.exceptions import ValidationAppError
from src.config import get_storage_settings

_DRIVE_LETTER = re.compile(r"^[A-Za-z]:")


def save_uploaded_file(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    relative_path: str,
    content: bytes,
    *,
    upload_root: Path | None = None,
) -> str:
    """Write ``content`` to disk and return the absolute filesystem path
    written. Raises ValidationAppError if ``relative_path`` is blank,
    absolute, or attempts to escape the task's own directory."""
    safe_path = _validate_relative_path(relative_path)

    root = upload_root if upload_root is not None else get_storage_settings().upload_root
    task_dir = Path(root) / str(user_id) / str(task_id)
    target = task_dir / safe_path

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return str(target)


def _validate_relative_path(relative_path: str) -> PurePosixPath:
    normalized = relative_path.replace("\\", "/").strip()
    if not normalized or _DRIVE_LETTER.match(normalized):
        raise ValidationAppError(f"invalid file path: {relative_path!r}")

    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ValidationAppError(f"invalid file path: {relative_path!r}")
    return path
