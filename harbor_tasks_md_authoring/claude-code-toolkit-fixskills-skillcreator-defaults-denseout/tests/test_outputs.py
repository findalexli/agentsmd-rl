"""Behavioral checks for claude-code-toolkit-fixskills-skillcreator-defaults-denseout (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert '**`user_invocable` default is `false`.** New skills are agent-facing by default:' in text, "expected to find: " + '**`user_invocable` default is `false`.** New skills are agent-facing by default:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert 'the `/do` router dispatches them, and the user never types the skill name. Emit' in text, "expected to find: " + 'the `/do` router dispatches them, and the user never types the skill name. Emit'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert 'This is a generation constraint on the outputs of this skill, not a style note' in text, "expected to find: " + 'This is a generation constraint on the outputs of this skill, not a style note'[:80]

