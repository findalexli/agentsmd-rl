"""Behavioral checks for vibe-remote-docsskills-refresh-vibe-remote-routing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-remote")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert '- keep the selected reasoning value compatible with the chosen model; common values are `low`, `medium`, and `high`, while `max` is only valid on supported models' in text, "expected to find: " + '- keep the selected reasoning value compatible with the chosen model; common values are `low`, `medium`, and `high`, while `max` is only valid on supported models'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert '- Claude reasoning is selected through `routing.claude_reasoning_effort`; common values are `low`, `medium`, and `high`, and some models also allow `max`.' in text, "expected to find: " + '- Claude reasoning is selected through `routing.claude_reasoning_effort`; common values are `low`, `medium`, and `high`, and some models also allow `max`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert '- If a Claude reasoning value is invalid for the chosen model, Vibe Remote drops that override and falls back to the backend default.' in text, "expected to find: " + '- If a Claude reasoning value is invalid for the chosen model, Vibe Remote drops that override and falls back to the backend default.'[:80]

