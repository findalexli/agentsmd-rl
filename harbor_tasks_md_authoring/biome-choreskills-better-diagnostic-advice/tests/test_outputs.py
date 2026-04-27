"""Behavioral checks for biome-choreskills-better-diagnostic-advice (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/biome")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/diagnostics-development/SKILL.md')
    assert '"Variables declared with "<Emphasis>"var"</Emphasis>" are function-scoped, not block-scoped, which means they can leak outside of loops and conditionals and cause unexpected behavior."' in text, "expected to find: " + '"Variables declared with "<Emphasis>"var"</Emphasis>" are function-scoped, not block-scoped, which means they can leak outside of loops and conditionals and cause unexpected behavior."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/diagnostics-development/SKILL.md')
    assert '"Consider using "<Emphasis>"let"</Emphasis>" or "<Emphasis>"const"</Emphasis>" instead."' in text, "expected to find: " + '"Consider using "<Emphasis>"let"</Emphasis>" or "<Emphasis>"const"</Emphasis>" instead."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/diagnostics-development/SKILL.md')
    assert '"Using "<Emphasis>"var"</Emphasis>" is not recommended."' in text, "expected to find: " + '"Using "<Emphasis>"var"</Emphasis>" is not recommended."'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert "If the rule has an `action()` to fix the issue, the 3rd message should go in the action's message. If not, it should go in the diagnostic's advice." in text, "expected to find: " + "If the rule has an `action()` to fix the issue, the 3rd message should go in the action's message. If not, it should go in the diagnostic's advice."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert "- Changesets are always required for new rules. New rules are `patch` level changes. There's a skill to help write good changesets." in text, "expected to find: " + "- Changesets are always required for new rules. New rules are `patch` level changes. There's a skill to help write good changesets."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert "// third message missing is bad, because it doesn't give users a clear path to fix the issue" in text, "expected to find: " + "// third message missing is bad, because it doesn't give users a clear path to fix the issue"[:80]

