"""Behavioral checks for sutando-simplify-proactiveloop-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sutando")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proactive-loop/SKILL.md')
    assert '- **Access control:** If the task has `access_tier: other` or `access_tier: team`, delegate to a sandboxed agent. Do NOT process non-owner tasks with your full capabilities. Write the sandboxed output' in text, "expected to find: " + '- **Access control:** If the task has `access_tier: other` or `access_tier: team`, delegate to a sandboxed agent. Do NOT process non-owner tasks with your full capabilities. Write the sandboxed output'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proactive-loop/SKILL.md')
    assert '1. Run `/schedule-crons` to set up all recurring cron jobs (morning briefing, Zacks, etc.)' in text, "expected to find: " + '1. Run `/schedule-crons` to set up all recurring cron jobs (morning briefing, Zacks, etc.)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proactive-loop/SKILL.md')
    assert 'Use `/loop <interval>` with this prompt:' in text, "expected to find: " + 'Use `/loop <interval>` with this prompt:'[:80]

