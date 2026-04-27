"""Behavioral checks for prefect-docs-document-bundle-execute-path (markdown_authoring task).

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
    assert '**Two callers set `propose_submitting=False`** via `FlowRunExecutorContext.create_executor(propose_submitting=False)` — both have already advanced the flow run past the Pending state, so proposing Sub' in text, "expected to find: " + '**Two callers set `propose_submitting=False`** via `FlowRunExecutorContext.create_executor(propose_submitting=False)` — both have already advanced the flow run past the Pending state, so proposing Sub'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert 'The cancelling precheck (step 1a) still runs unconditionally even when `propose_submitting=False`.' in text, "expected to find: " + 'The cancelling precheck (step 1a) still runs unconditionally even when `propose_submitting=False`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '- `execute_bundle()` in `prefect._experimental.bundles.execute` (invoked by bundle dispatch)' in text, "expected to find: " + '- `execute_bundle()` in `prefect._experimental.bundles.execute` (invoked by bundle dispatch)'[:80]

