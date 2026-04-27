"""Behavioral checks for prefect-update-agentsmd-files-for-6f57ee5 (markdown_authoring task).

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
    assert 'The events page displays at most 50 events in descending chronological order. In busy CI environments, parallel shards generate background events (deployment runs, work-pool polls, etc.) that can push' in text, "expected to find: " + 'The events page displays at most 50 events in descending chronological order. In busy CI environments, parallel shards generate background events (deployment runs, work-pool polls, etc.) that can push'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'Pass the resource IDs (or prefixes) of the resources your test cares about. This keeps the result set small regardless of how much background activity other shards produce.' in text, "expected to find: " + 'Pass the resource IDs (or prefixes) of the resources your test cares about. This keeps the result set small regardless of how much background activity other shards produce.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'Scope events-page tests to specific resources using the `resource` query parameter:' in text, "expected to find: " + 'Scope events-page tests to specific resources using the `resource` query parameter:'[:80]

