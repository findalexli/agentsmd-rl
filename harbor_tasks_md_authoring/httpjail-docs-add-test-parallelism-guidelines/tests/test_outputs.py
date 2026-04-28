"""Behavioral checks for httpjail-docs-add-test-parallelism-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/httpjail")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Integration tests should run in parallel by default.** The jails are designed to be independent from each other, so the test suite should leverage good parallelism. Tests should only be marked as se' in text, "expected to find: " + '**Integration tests should run in parallel by default.** The jails are designed to be independent from each other, so the test suite should leverage good parallelism. Tests should only be marked as se'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Each jail operates in its own network namespace (on Linux) or with its own proxy port, so most tests can safely run concurrently. This significantly reduces total test runtime.' in text, "expected to find: " + 'Each jail operates in its own network namespace (on Linux) or with its own proxy port, so most tests can safely run concurrently. This significantly reduces total test runtime.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- System-wide firewall rules that can't be isolated" in text, "expected to find: " + "- System-wide firewall rules that can't be isolated"[:80]

