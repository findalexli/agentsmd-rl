"""Behavioral checks for libretto-fix-check-action-log-before (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the br' in text, "expected to find: " + '2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the br'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/libretto/skill/SKILL.md')
    assert '2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the br' in text, "expected to find: " + '2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the br'[:80]

