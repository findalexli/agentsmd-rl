"""Behavioral checks for gitbutler-docsskill-encourage-proactive-committing-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gitbutler")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/but/skill/SKILL.md')
    assert "4. **Commit early and often** - don't wait for perfection. Unlike traditional git, GitButler makes editing history trivial with `absorb`, `squash`, and `reword`. It's better to have small, atomic comm" in text, "expected to find: " + "4. **Commit early and often** - don't wait for perfection. Unlike traditional git, GitButler makes editing history trivial with `absorb`, `squash`, and `reword`. It's better to have small, atomic comm"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/but/skill/SKILL.md')
    assert "**Commit early, commit often.** Don't hesitate to create commits - GitButler makes editing history trivial. You can always `squash`, `reword`, or `absorb` changes into existing commits later. Small at" in text, "expected to find: " + "**Commit early, commit often.** Don't hesitate to create commits - GitButler makes editing history trivial. You can always `squash`, `reword`, or `absorb` changes into existing commits later. Small at"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/but/skill/SKILL.md')
    assert 'but diff --json             # See hunk IDs when a file has multiple changes' in text, "expected to find: " + 'but diff --json             # See hunk IDs when a file has multiple changes'[:80]

