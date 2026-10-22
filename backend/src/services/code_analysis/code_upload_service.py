"""CodeUploadService (T069): validate, store, and analyze an uploaded set
of code files for a Task — covers all three upload methods (file, folder,
paste; FR-005..FR-007).

Everything is validated (extension, size, not-binary, overall file count)
before anything is written — a bad upload fails cleanly with
ValidationAppError and leaves no partial state on disk or in the DB.
Once validated: each file is stored to disk via file_storage (T067), the
project's dominant language is detected (T065), and aggregate complexity
is assessed (T066) over every file's content decoded as UTF-8
(errors="replace" — uploaded text files aren't guaranteed to be strictly
UTF-8). The result is one UploadedCode row (at most one per task, per the
`unique=True` constraint on task_id) plus one CodeFile row per file.
"""

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.exceptions import NotFoundError, ValidationAppError
from src.models.code_file import CodeFile
from src.models.uploaded_code import UploadedCode
from src.services.code_analysis import file_storage
from src.services.code_analysis.complexity_analyzer import analyze_project_complexity
from src.services.code_analysis.language_detector import detect_project_language
from src.services.task_service import TaskService
from src.utils import file_validator

# Treated as a single file upload for the "paste" method — not a real
# user-supplied filename, so always this fixed name/extension.
PASTE_FILENAME = "pasted_code.txt"

_UPLOAD_METHODS = ("file", "folder", "paste")

# (filename, relative_path, content) — relative_path is None for a flat
# upload (single file / each file in a multi-file "file" upload), and the
# full folder-relative path (e.g. "src/main.py") for a "folder" upload.
UploadEntry = tuple[str, str | None, bytes]


class CodeUploadService:
    def __init__(self, db: AsyncSession, *, upload_root: Path | None = None) -> None:
        self.db = db
        self._upload_root = upload_root

    async def upload(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        upload_method: str,
        *,
        files: list[UploadEntry] | None = None,
        pasted_code: str | None = None,
    ) -> UploadedCode:
        """Validate, store, and analyze an upload for ``task_id``. Raises
        ValidationAppError on any validation failure (nothing is written
        in that case), or NotFoundError if the task isn't owned by
        ``user_id``."""
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        entries = self._resolve_entries(upload_method, files, pasted_code)

        file_validator.validate_file_count(len(entries))
        for filename, _relative_path, content in entries:
            file_validator.validate_extension(filename)
            file_validator.validate_size(len(content))
            file_validator.validate_not_binary(content)

        return await self._store_and_analyze(task_id, user_id, entries)

    async def get_for_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> UploadedCode:
        """Fetch the task's UploadedCode (with its CodeFiles eagerly
        loaded). Raises NotFoundError if the task isn't owned by
        ``user_id`` or has no uploaded code yet."""
        await TaskService(self.db).get(task_id, user_id)  # ownership + 404

        result = await self.db.execute(
            select(UploadedCode)
            .where(UploadedCode.task_id == task_id)
            .options(selectinload(UploadedCode.code_files))
        )
        uploaded_code = result.scalar_one_or_none()
        if uploaded_code is None:
            raise NotFoundError("uploaded code not found for this task")
        return uploaded_code

    def _resolve_entries(
        self,
        upload_method: str,
        files: list[UploadEntry] | None,
        pasted_code: str | None,
    ) -> list[UploadEntry]:
        if upload_method == "paste":
            if not pasted_code or not pasted_code.strip():
                raise ValidationAppError("pasted_code is required for the paste upload method")
            return [(PASTE_FILENAME, None, pasted_code.encode("utf-8"))]

        if upload_method not in _UPLOAD_METHODS:
            raise ValidationAppError(f"unsupported upload method: {upload_method!r}")

        if not files:
            raise ValidationAppError("at least one file is required")
        return files

    async def _store_and_analyze(
        self, task_id: uuid.UUID, user_id: uuid.UUID, entries: list[UploadEntry]
    ) -> UploadedCode:
        stored_paths = [
            file_storage.save_uploaded_file(
                user_id,
                task_id,
                relative_path or filename,
                content,
                upload_root=self._upload_root,
            )
            for filename, relative_path, content in entries
        ]

        filenames = [filename for filename, _, _ in entries]
        decoded_contents = [content.decode("utf-8", errors="replace") for _, _, content in entries]
        total_size = sum(len(content) for _, _, content in entries)

        complexity = analyze_project_complexity(decoded_contents)
        uploaded_code = UploadedCode(
            task_id=task_id,
            detected_language=detect_project_language(filenames),
            complexity_level=complexity.level,
            total_lines=complexity.total_lines,
            total_files=len(entries),
            upload_size_bytes=total_size,
        )
        self.db.add(uploaded_code)
        await self.db.flush()

        for (filename, relative_path, content), storage_path in zip(
            entries, stored_paths, strict=False
        ):
            self.db.add(
                CodeFile(
                    uploaded_code_id=uploaded_code.id,
                    file_name=filename,
                    file_path=relative_path,
                    file_extension=Path(filename).suffix.lower() or None,
                    file_size_bytes=len(content),
                    storage_path=storage_path,
                )
            )
        await self.db.flush()
        await self.db.refresh(uploaded_code, attribute_names=["code_files"])
        return uploaded_code
