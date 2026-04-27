"""Behavioral checks for prefect-update-agentsmd-files-for-9551bb8 (markdown_authoring task).

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
    assert '`Runner.add_flow()` explicitly assigns `deployment.work_pool_name = None` and `deployment.work_queue_name = None` *after* the `RunnerDeployment` is constructed, not via constructor kwargs. This is int' in text, "expected to find: " + '`Runner.add_flow()` explicitly assigns `deployment.work_pool_name = None` and `deployment.work_queue_name = None` *after* the `RunnerDeployment` is constructed, not via constructor kwargs. This is int'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '## Work Pool Clearing in `add_flow`' in text, "expected to find: " + '## Work Pool Clearing in `add_flow`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/server/AGENTS.md')
    assert '- **`update_deployment` uses `model_fields_set` to distinguish explicit `None` from "not provided" for `work_pool_name`.** In `models/deployments.py`, when `deployment.work_pool_name is None` AND `"wo' in text, "expected to find: " + '- **`update_deployment` uses `model_fields_set` to distinguish explicit `None` from "not provided" for `work_pool_name`.** In `models/deployments.py`, when `deployment.work_pool_name is None` AND `"wo'[:80]

