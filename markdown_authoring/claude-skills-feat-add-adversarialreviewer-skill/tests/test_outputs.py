"""Behavioral checks for claude-skills-feat-add-adversarialreviewer-skill (markdown_authoring task).

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
    text = _read('engineering-team/adversarial-reviewer/SKILL.md')
    assert 'description: "Adversarial code review that breaks the self-review monoculture. Use when you want a genuinely critical review of recent changes, before merging a PR, or when you suspect Claude is being' in text, "expected to find: " + 'description: "Adversarial code review that breaks the self-review monoculture. Use when you want a genuinely critical review of recent changes, before merging a PR, or when you suspect Claude is being'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering-team/adversarial-reviewer/SKILL.md')
    assert 'When Claude reviews code it wrote (or code it just read), it shares the same mental model, assumptions, and blind spots as the author. This produces "Looks good to me" reviews on code that a fresh hum' in text, "expected to find: " + 'When Claude reviews code it wrote (or code it just read), it shares the same mental model, assumptions, and blind spots as the author. This produces "Looks good to me" reviews on code that a fresh hum'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering-team/adversarial-reviewer/SKILL.md')
    assert 'You are likely reviewing code you just wrote or just read. Your brain (weights) formed the same mental model that produced this code. You will naturally think it looks correct because it matches your ' in text, "expected to find: " + 'You are likely reviewing code you just wrote or just read. Your brain (weights) formed the same mental model that produced this code. You will naturally think it looks correct because it matches your '[:80]

