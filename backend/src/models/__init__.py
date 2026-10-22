"""Import every model class here so that importing *any* `src.models.*`
submodule (e.g. `from src.models.project import Project`) first runs this
package's __init__ — which, as a side effect, imports every other model
too, registering all of them in SQLAlchemy's class registry before any
mapper gets configured.

Why this matters: several models declare relationships to each other by
string name (e.g. `Project.user: Mapped["User"] = relationship(...)`,
resolved lazily under `TYPE_CHECKING` to avoid circular imports — see each
model's docstring). SQLAlchemy only resolves those strings the first time
it actually configures a mapper (the first real query), and only classes
that have been imported *somewhere* in the current process by then are
visible to it.

Inside the full pytest suite this is invisible: dozens of test files
import different models across hundreds of tests in the same process, so
by the time any one test queries the DB, everything happens to already be
registered. It only surfaces in a process that imports a narrower slice —
most importantly, a real `celery -A src.tasks.celery_app worker`, which
imports only `src.tasks.document_generation` and its own dependency chain
(DocumentGenerationService -> TaskService, which imports Project/CodeFile/
UploadedCode but not User) before executing a task. That chain doesn't
happen to import `src.models.user`, so the first query — `Task.project`
-> `Project.user` — fails with "expression 'User' failed to locate a
name" (found via manual E2E testing: the Celery worker crashed on every
real document-generation task). See
tests/unit/test_celery_worker_import_isolation.py for the regression
test (spawns a subprocess to reproduce the worker's narrower import
graph, since importing everything in-process, like this file now does,
would otherwise mask the same bug in tests too).
"""

from src.models.code_file import CodeFile
from src.models.learning_document import LearningDocument
from src.models.project import Project
from src.models.refresh_token import RefreshToken
from src.models.task import Task
from src.models.uploaded_code import UploadedCode
from src.models.user import User

__all__ = [
    "CodeFile",
    "LearningDocument",
    "Project",
    "RefreshToken",
    "Task",
    "UploadedCode",
    "User",
]
