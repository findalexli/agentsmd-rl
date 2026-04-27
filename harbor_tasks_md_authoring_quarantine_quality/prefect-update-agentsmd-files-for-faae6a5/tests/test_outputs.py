"""Behavioral checks for prefect-update-agentsmd-files-for-faae6a5 (markdown_authoring task).

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
    text = _read('src/prefect/runner/AGENTS.md')
    assert '`ScheduledRunPoller` now calls `propose_pending` (Scheduled → Pending) before handing off to `FlowRunExecutor`. `FlowRunExecutor` then calls `propose_submitting` (Pending → Submitting sub-state) as st' in text, "expected to find: " + '`ScheduledRunPoller` now calls `propose_pending` (Scheduled → Pending) before handing off to `FlowRunExecutor`. `FlowRunExecutor` then calls `propose_submitting` (Pending → Submitting sub-state) as st'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert 'ProcessWorker (src/prefect/workers/process.py) calls `Runner.execute_flow_run()` and `Runner.execute_bundle()` via the deprecated path, suppressing `PrefectDeprecationWarning` with `warnings.catch_war' in text, "expected to find: " + 'ProcessWorker (src/prefect/workers/process.py) calls `Runner.execute_flow_run()` and `Runner.execute_bundle()` via the deprecated path, suppressing `PrefectDeprecationWarning` with `warnings.catch_war'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert 'These will be removed once internal callers (notably ProcessWorker) are migrated. ProcessWorker currently suppresses the deprecation warnings via `warnings.catch_warnings()`.' in text, "expected to find: " + 'These will be removed once internal callers (notably ProcessWorker) are migrated. ProcessWorker currently suppresses the deprecation warnings via `warnings.catch_warnings()`.'[:80]

