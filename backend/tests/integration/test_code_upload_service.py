"""Integration tests for CodeUploadService (T069) — run against the real
database (see tests/conftest.py's db_session fixture), because the
behaviors that matter (UploadedCode/CodeFile rows actually persisting,
the task_id uniqueness constraint) are DB-level guarantees.

Every test passes an explicit `upload_root` (pytest tmp_path) so files are
never written to the real storage/uploads directory.
"""

import uuid

import pytest

from src.api.exceptions import ValidationAppError
from src.models.uploaded_code import UploadedCode
from src.models.user import User
from src.services.code_analysis.code_upload_service import CodeUploadService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils.file_validator import MAX_FILES_PER_UPLOAD
from src.utils.security import hash_password


async def _make_task(db_session, email: str):
    user = User(email=email, password_hash=hash_password("correct-horse-123"))
    db_session.add(user)
    await db_session.flush()
    project = await ProjectService(db_session).create(user.id, "Project")
    task = await TaskService(db_session).create(project.id, user.id, "A Task", upload_method="file")
    return user, task


# ---------------------------------------------------------------------------
# upload() with a "file" upload
# ---------------------------------------------------------------------------


async def test_upload_file_persists_uploaded_code_and_code_file(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-ok@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    uploaded_code = await service.upload(
        task.id,
        user.id,
        "file",
        files=[("main.py", None, b"def hello():\n    print('hi')\n")],
    )

    assert uploaded_code.task_id == task.id
    assert uploaded_code.detected_language == "python"
    assert uploaded_code.total_files == 1
    assert uploaded_code.total_lines == 2
    assert uploaded_code.upload_size_bytes == len(b"def hello():\n    print('hi')\n")
    assert uploaded_code.complexity_level == "beginner"


async def test_upload_file_writes_content_to_disk(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-disk@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    await service.upload(task.id, user.id, "file", files=[("main.py", None, b"x = 1\n")])

    expected = tmp_path / str(user.id) / str(task.id) / "main.py"
    assert expected.read_bytes() == b"x = 1\n"


async def test_upload_file_creates_one_code_file_row_per_file(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-multi@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    uploaded_code = await service.upload(
        task.id,
        user.id,
        "file",
        files=[
            ("main.py", None, b"x = 1\n"),
            ("utils.py", None, b"y = 2\n"),
        ],
    )

    file_names = {f.file_name for f in uploaded_code.code_files}
    assert file_names == {"main.py", "utils.py"}
    assert all(f.storage_path for f in uploaded_code.code_files)


async def test_upload_folder_sets_file_path_for_nested_files(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-folder@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    uploaded_code = await service.upload(
        task.id,
        user.id,
        "folder",
        files=[("main.py", "src/main.py", b"x = 1\n")],
    )

    code_file = uploaded_code.code_files[0]
    assert code_file.file_name == "main.py"
    assert code_file.file_path == "src/main.py"
    expected = tmp_path / str(user.id) / str(task.id) / "src" / "main.py"
    assert expected.read_bytes() == b"x = 1\n"


async def test_upload_rejects_unsupported_extension_without_writing_anything(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-badext@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "file", files=[("image.png", None, b"\x89PNG\r\n")])

    assert not any((tmp_path / str(user.id)).glob("**/*"))


async def test_upload_rejects_binary_content(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-binary@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "file", files=[("main.py", None, b"\x00binary")])


async def test_upload_rejects_too_many_files(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-toomany@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)
    files = [(f"f{i}.py", None, b"x = 1\n") for i in range(MAX_FILES_PER_UPLOAD + 1)]

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "file", files=files)


async def test_upload_rejects_no_files(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-nofiles@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "file", files=[])


async def test_upload_rejects_unsupported_upload_method(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-badmethod@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "ftp", files=[("main.py", None, b"x = 1\n")])


# ---------------------------------------------------------------------------
# upload() with "paste"
# ---------------------------------------------------------------------------


async def test_upload_paste_persists_uploaded_code_as_single_file(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-paste@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    uploaded_code = await service.upload(task.id, user.id, "paste", pasted_code="print('hello')\n")

    # Pasted code is stored as a fixed pasted_code.txt filename, so
    # language detection resolves by extension (.txt -> "text") rather
    # than by content — detecting the actual language from a snippet
    # without any file extension hint is out of scope for this task.
    assert uploaded_code.total_files == 1
    assert len(uploaded_code.code_files) == 1
    assert uploaded_code.detected_language == "text"


async def test_upload_paste_rejects_blank_code(db_session, tmp_path):
    user, task = await _make_task(db_session, "upload-pasteblank@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    with pytest.raises(ValidationAppError):
        await service.upload(task.id, user.id, "paste", pasted_code="   ")


# ---------------------------------------------------------------------------
# get_for_task()
# ---------------------------------------------------------------------------


async def test_get_for_task_returns_uploaded_code_with_code_files(db_session, tmp_path):
    user, task = await _make_task(db_session, "get-ok@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)
    await service.upload(task.id, user.id, "file", files=[("main.py", None, b"x = 1\n")])

    fetched = await service.get_for_task(task.id, user.id)

    assert fetched.task_id == task.id
    assert len(fetched.code_files) == 1


async def test_get_for_task_raises_not_found_when_no_upload_exists(db_session, tmp_path):
    user, task = await _make_task(db_session, "get-none@example.com")
    service = CodeUploadService(db_session, upload_root=tmp_path)

    from src.api.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await service.get_for_task(task.id, user.id)


async def test_get_for_task_raises_not_found_for_non_owner(db_session, tmp_path):
    user, task = await _make_task(db_session, "get-owner@example.com")
    stranger = User(email="get-stranger@example.com", password_hash=hash_password("x"))
    db_session.add(stranger)
    await db_session.flush()
    service = CodeUploadService(db_session, upload_root=tmp_path)
    await service.upload(task.id, user.id, "file", files=[("main.py", None, b"x = 1\n")])

    from src.api.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await service.get_for_task(task.id, stranger.id)
