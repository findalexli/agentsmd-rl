"""Behavioral checks for cultivation-world-simulator-feat-add-specinterview-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cultivation-world-simulator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/spec-interview/SKILL.md')
    assert '1. **Use your judgment** - Adapt question depth and focus based on the topic. A small UI change needs different questions than a new authentication system.' in text, "expected to find: " + '1. **Use your judgment** - Adapt question depth and focus based on the topic. A small UI change needs different questions than a new authentication system.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/spec-interview/SKILL.md')
    assert "Write the spec to `docs/specs/<feature-name>.md` (or ask user for preferred path). Include whatever sections are relevant — don't force a rigid template." in text, "expected to find: " + "Write the spec to `docs/specs/<feature-name>.md` (or ask user for preferred path). Include whatever sections are relevant — don't force a rigid template."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/spec-interview/SKILL.md')
    assert 'Conduct a thorough interview using `AskUserQuestion` to deeply understand a feature, system, or idea before writing a specification document.' in text, "expected to find: " + 'Conduct a thorough interview using `AskUserQuestion` to deeply understand a feature, system, or idea before writing a specification document.'[:80]

