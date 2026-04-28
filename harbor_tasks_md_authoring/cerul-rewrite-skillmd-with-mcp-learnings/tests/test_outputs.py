"""Behavioral checks for cerul-rewrite-skillmd-with-mcp-learnings (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cerul")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cerul/SKILL.md')
    assert 'description: You cannot access video content on your own. Use Cerul to search what was said, shown, or presented in tech talks, podcasts, conference presentations, and earnings calls. Use when a user ' in text, "expected to find: " + 'description: You cannot access video content on your own. Use Cerul to search what was said, shown, or presented in tech talks, podcasts, conference presentations, and earnings calls. Use when a user '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cerul/SKILL.md')
    assert 'The `speaker` field often contains the **channel name** (e.g. "Sequoia Capital", "a16z", "Lex Fridman") rather than the interviewee name. If a speaker filter returns no results, **retry without it** a' in text, "expected to find: " + 'The `speaker` field often contains the **channel name** (e.g. "Sequoia Capital", "a16z", "Lex Fridman") rather than the interviewee name. If a speaker filter returns no results, **retry without it** a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cerul/SKILL.md')
    assert 'You cannot watch videos, listen to talks, or read transcripts on your own. Cerul gives you that ability. Use it whenever the user asks about what someone said, presented, or showed in a video — do not' in text, "expected to find: " + 'You cannot watch videos, listen to talks, or read transcripts on your own. Cerul gives you that ability. Use it whenever the user asks about what someone said, presented, or showed in a video — do not'[:80]

