"""Behavioral checks for zoonk-choreagents-clean-up-unused-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zoonk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/zoonk-code-simplification/SKILL.md')
    assert '.agents/skills/zoonk-code-simplification/SKILL.md' in text, "expected to find: " + '.agents/skills/zoonk-code-simplification/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/zoonk-issue-writer/SKILL.md')
    assert '.agents/skills/zoonk-issue-writer/SKILL.md' in text, "expected to find: " + '.agents/skills/zoonk-issue-writer/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/zoonk-technical/SKILL.md')
    assert '.agents/skills/zoonk-technical/SKILL.md' in text, "expected to find: " + '.agents/skills/zoonk-technical/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-simplifier.md')
    assert '.claude/agents/code-simplifier.md' in text, "expected to find: " + '.claude/agents/code-simplifier.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/prompt-reviewer.md')
    assert '.claude/agents/prompt-reviewer.md' in text, "expected to find: " + '.claude/agents/prompt-reviewer.md'[:80]

