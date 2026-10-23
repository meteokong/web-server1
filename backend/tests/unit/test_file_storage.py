"""Unit tests for the file storage service (T067): persist uploaded code
file content under storage/uploads/{user_id}/{task_id}/{relative_path},
with path-traversal protection for the (user-controlled) relative path.

All tests pass an explicit `upload_root` (a pytest tmp_path) so they never
touch the real storage/uploads directory.
"""

import uuid

import pytest

from src.api.exceptions import ValidationAppError
from src.config import get_storage_settings
from src.services.code_analysis.file_storage import save_uploaded_file


def test_save_uploaded_file_writes_content_under_user_and_task_dirs(tmp_path):
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    path = save_uploaded_file(user_id, task_id, "main.py", b"print('hi')", upload_root=tmp_path)

    expected = tmp_path / str(user_id) / str(task_id) / "main.py"
    assert path == str(expected)
    assert expected.read_bytes() == b"print('hi')"


def test_save_uploaded_file_creates_nested_directories_for_folder_uploads(tmp_path):
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    path = save_uploaded_file(
        user_id, task_id, "src/utils/helpers.py", b"x = 1", upload_root=tmp_path
    )

    expected = tmp_path / str(user_id) / str(task_id) / "src" / "utils" / "helpers.py"
    assert path == str(expected)
    assert expected.read_bytes() == b"x = 1"


@pytest.mark.parametrize(
    "relative_path",
    [
        "../../etc/passwd",
        "sub/../../escape.py",
        "/etc/passwd",
        "C:/Windows/System32/evil.py",
        "C:\\Windows\\System32\\evil.py",
        "",
        "   ",
    ],
)
def test_save_uploaded_file_rejects_path_traversal_and_absolute_paths(tmp_path, relative_path):
    with pytest.raises(ValidationAppError):
        save_uploaded_file(uuid.uuid4(), uuid.uuid4(), relative_path, b"x", upload_root=tmp_path)


def test_save_uploaded_file_isolates_different_tasks_and_users(tmp_path):
    user_a, user_b = uuid.uuid4(), uuid.uuid4()
    task_a, task_b = uuid.uuid4(), uuid.uuid4()

    path_a = save_uploaded_file(user_a, task_a, "main.py", b"a", upload_root=tmp_path)
    path_b = save_uploaded_file(user_b, task_b, "main.py", b"b", upload_root=tmp_path)

    assert path_a != path_b
    assert (tmp_path / str(user_a) / str(task_a) / "main.py").read_bytes() == b"a"
    assert (tmp_path / str(user_b) / str(task_b) / "main.py").read_bytes() == b"b"


def test_save_uploaded_file_defaults_to_configured_upload_root(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    get_storage_settings.cache_clear()
    user_id, task_id = uuid.uuid4(), uuid.uuid4()

    path = save_uploaded_file(user_id, task_id, "main.py", b"x")

    assert path == str(tmp_path / str(user_id) / str(task_id) / "main.py")
    get_storage_settings.cache_clear()
