"""Behavioral checks for prefect-update-agentsmd-files-for-c5b1fdd (markdown_authoring task).

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
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'Comparing a count captured before an action to a count captured after the action is flaky in parallel CI: other shards continuously emit background events (work-pool polls, heartbeats, etc.), so the "' in text, "expected to find: " + 'Comparing a count captured before an action to a count captured after the action is flaky in parallel CI: other shards continuously emit background events (work-pool polls, heartbeats, etc.), so the "'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '// ❌ Bad - flaky: background events can push the post-action count above the pre-action count' in text, "expected to find: " + '// ❌ Bad - flaky: background events can push the post-action count above the pre-action count'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'const prefix = "prefect.flow-run"; // strip trailing ".*" from the filter label' in text, "expected to find: " + 'const prefix = "prefect.flow-run"; // strip trailing ".*" from the filter label'[:80]

