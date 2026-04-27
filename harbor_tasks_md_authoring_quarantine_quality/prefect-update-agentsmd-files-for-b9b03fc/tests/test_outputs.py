"""Behavioral checks for prefect-update-agentsmd-files-for-b9b03fc (markdown_authoring task).

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
    text = _read('src/prefect/AGENTS.md')
    assert '- `workers/` → Work-pool-based execution layer: polls for flow runs, dispatches to infrastructure (see workers/AGENTS.md)' in text, "expected to find: " + '- `workers/` → Work-pool-based execution layer: polls for flow runs, dispatches to infrastructure (see workers/AGENTS.md)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert '- `ProcessWorker` calls the deprecated `Runner.execute_flow_run()` / `Runner.execute_bundle()` paths (suppressing `PrefectDeprecationWarning` with `warnings.catch_warnings()`). It bypasses `FlowRunExe' in text, "expected to find: " + '- `ProcessWorker` calls the deprecated `Runner.execute_flow_run()` / `Runner.execute_bundle()` paths (suppressing `PrefectDeprecationWarning` with `warnings.catch_warnings()`). It bypasses `FlowRunExe'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert 'Workers are long-running processes that pull scheduled flow runs from a work pool and dispatch them to infrastructure (processes, Docker, Kubernetes, cloud VMs, etc.). Each worker type subclasses `Bas' in text, "expected to find: " + 'Workers are long-running processes that pull scheduled flow runs from a work pool and dispatch them to infrastructure (processes, Docker, Kubernetes, cloud VMs, etc.). Each worker type subclasses `Bas'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert '**Teardown guard**: `teardown()` only removes these vars if they still match the current worker instance (`os.environ.get("PREFECT__WORKER_NAME") == self.name`). This prevents a second worker sharing ' in text, "expected to find: " + '**Teardown guard**: `teardown()` only removes these vars if they still match the current worker instance (`os.environ.get("PREFECT__WORKER_NAME") == self.name`). This prevents a second worker sharing '[:80]

