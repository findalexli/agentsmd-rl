"""Behavioral checks for effection-add-gitmoji-directive-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/effection")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'changes to files that direct the behavior of AI such as AGENTS.md or llms.txt' in text, "expected to find: " + 'changes to files that direct the behavior of AI such as AGENTS.md or llms.txt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use [gitmoji](https://gitmoji.dev) for commit and pull request subjects. For' in text, "expected to find: " + 'Use [gitmoji](https://gitmoji.dev) for commit and pull request subjects. For'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'use a robot emoji instead of the standard gitmoji for documentation' in text, "expected to find: " + 'use a robot emoji instead of the standard gitmoji for documentation'[:80]

