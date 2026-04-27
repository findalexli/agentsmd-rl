"""Behavioral checks for claude-skills-exploringcodebases-v221-goodbad-batching-examp (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert '# BAD — three scans, three answers (3× the cost for the same information)' in text, "expected to find: " + '# BAD — three scans, three answers (3× the cost for the same information)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert 'call pays the full scan cost. Multiple queries added to the same command' in text, "expected to find: " + 'call pays the full scan cost. Multiple queries added to the same command'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert "share that scan and each additional query adds ~0ms. If you're about to" in text, "expected to find: " + "share that scan and each additional query adds ~0ms. If you're about to"[:80]

