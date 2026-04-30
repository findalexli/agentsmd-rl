"""Behavioral checks for prefect-update-agentsmd-files-for-38cb60b (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/client/AGENTS.md')
    assert '- **Task-run submission schemas must be eagerly rebuilt.** Schemas instantiated on the concurrent submission path (`Task.create_local_run()`) are rebuilt at import time via `model_rebuild()` at the bo' in text, "expected to find: " + '- **Task-run submission schemas must be eagerly rebuilt.** Schemas instantiated on the concurrent submission path (`Task.create_local_run()`) are rebuilt at import time via `model_rebuild()` at the bo'[:80]

