"""Behavioral checks for worktrunk-docstend-deflect-niche-feature-requests (markdown_authoring task).

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
    assert "- The request benefits a small subset of users or a single reporter's workflow" in text, "expected to find: " + "- The request benefits a small subset of users or a single reporter's workflow"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert '- The behavior can be composed from existing `wt` commands or shell primitives' in text, "expected to find: " + '- The behavior can be composed from existing `wt` commands or shell primitives'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert '2. Test it in a scratch worktree — verify it works for the happy path and edge' in text, "expected to find: " + '2. Test it in a scratch worktree — verify it works for the happy path and edge'[:80]

