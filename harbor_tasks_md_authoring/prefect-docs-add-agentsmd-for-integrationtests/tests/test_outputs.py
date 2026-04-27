"""Behavioral checks for prefect-docs-add-agentsmd-for-integrationtests (markdown_authoring task).

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
    text = _read('integration-tests/AGENTS.md')
    assert "**Poll, don't assert synchronously.** Hook execution, state transitions, and marker-file writes are independent side effects of the same cancel/complete sequence — the API state can become visible bef" in text, "expected to find: " + "**Poll, don't assert synchronously.** Hook execution, state transitions, and marker-file writes are independent side effects of the same cancel/complete sequence — the API state can become visible bef"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('integration-tests/AGENTS.md')
    assert '**Marker files for cross-process state.** Flows running in subprocesses write files to a shared `tmp_path` to signal that a state was reached. Name markers with constants (`PARENT_HOOK_MARKER`, `CHILD' in text, "expected to find: " + '**Marker files for cross-process state.** Flows running in subprocesses write files to a shared `tmp_path` to signal that a state was reached. Name markers with constants (`PARENT_HOOK_MARKER`, `CHILD'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('integration-tests/AGENTS.md')
    assert 'These tests cover scenarios that unit tests cannot: real server ↔ worker communication, subprocess flow execution, cancellation across process boundaries, event delivery, and scheduling statefulness.' in text, "expected to find: " + 'These tests cover scenarios that unit tests cannot: real server ↔ worker communication, subprocess flow execution, cancellation across process boundaries, event delivery, and scheduling statefulness.'[:80]

