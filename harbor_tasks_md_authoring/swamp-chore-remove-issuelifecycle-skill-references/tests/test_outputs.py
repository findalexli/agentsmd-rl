"""Behavioral checks for swamp-chore-remove-issuelifecycle-skill-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swamp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-lifecycle/SKILL.md')
    assert '.claude/skills/issue-lifecycle/SKILL.md' in text, "expected to find: " + '.claude/skills/issue-lifecycle/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-lifecycle/references/adversarial-review.md')
    assert '.claude/skills/issue-lifecycle/references/adversarial-review.md' in text, "expected to find: " + '.claude/skills/issue-lifecycle/references/adversarial-review.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-lifecycle/references/implementation.md')
    assert '.claude/skills/issue-lifecycle/references/implementation.md' in text, "expected to find: " + '.claude/skills/issue-lifecycle/references/implementation.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-lifecycle/references/planning.md')
    assert '.claude/skills/issue-lifecycle/references/planning.md' in text, "expected to find: " + '.claude/skills/issue-lifecycle/references/planning.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-lifecycle/references/triage.md')
    assert '.claude/skills/issue-lifecycle/references/triage.md' in text, "expected to find: " + '.claude/skills/issue-lifecycle/references/triage.md'[:80]

