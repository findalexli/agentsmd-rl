"""Behavioral checks for worktrunk-add-weekly-statusline-cachecheck-task (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/worktrunk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'running `wt-perf cache-check` against a real `wt list statusline --claude-code`' in text, "expected to find: " + 'running `wt-perf cache-check` against a real `wt list statusline --claude-code`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert "- **Legitimate** (different cwd, different ref form that can't be normalized," in text, "expected to find: " + "- **Legitimate** (different cwd, different ref form that can't be normalized,"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'Detect new in-process cache-miss duplicates introduced by recent changes by' in text, "expected to find: " + 'Detect new in-process cache-miss duplicates introduced by recent changes by'[:80]

