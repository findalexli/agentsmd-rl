"""Behavioral checks for server-docs-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use TDD by default: write a failing test, verify it fails for the right reason, pass it in the simplest way, then refactor. If asked to implement without a test, confirm whether to skip it.' in text, "expected to find: " + '- Use TDD by default: write a failing test, verify it fails for the right reason, pass it in the simplest way, then refactor. If asked to implement without a test, confirm whether to skip it.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- A passing test suite is not proof of correctness — before committing, review affected user flows in the codebase to check for regressions' in text, "expected to find: " + '- A passing test suite is not proof of correctness — before committing, review affected user flows in the codebase to check for regressions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Before considering a task done, remove any scaffolding, debug logs, or temporary code added during implementation' in text, "expected to find: " + '- Before considering a task done, remove any scaffolding, debug logs, or temporary code added during implementation'[:80]

