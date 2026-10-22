"""Regression test for a mapper-configuration bug found during manual E2E
testing: a real `celery -A src.tasks.celery_app worker` process only
imports `src.tasks.document_generation` (plus whatever it imports
transitively) before executing a task — unlike the pytest suite, which
accumulates imports of every model module across every test file in the
same process, masking any module that forgets to import a model it needs.

`src.tasks.document_generation` -> DocumentGenerationService ->
TaskService imports Project/CodeFile/UploadedCode, but nothing in that
chain imports `User` — so SQLAlchemy's string-based relationship
resolution (`Task.project` -> `Project.user`) fails the first time a
mapper actually gets configured, with "expression 'User' failed to
locate a name". This only reproduces in a *fresh* process (mirroring the
real worker), which is why this test spawns a subprocess instead of just
importing the module directly.
"""

import subprocess
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parents[2]


def test_importing_document_generation_task_alone_configures_mappers_cleanly():
    """Mirrors what `celery -A src.tasks.celery_app worker` actually
    imports before running a task: just this one module. Configuring all
    mappers afterward (what the first real query does) must not raise."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import src.tasks.document_generation; "
            "from sqlalchemy.orm import configure_mappers; "
            "configure_mappers()",
        ],
        capture_output=True,
        text=True,
        cwd=str(_BACKEND_DIR),
    )

    assert result.returncode == 0, result.stderr
