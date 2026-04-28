"""Behavioral checks for continuous-claude-v3-fix-formatting-of-description-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/continuous-claude-v3")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/completion-check/SKILL.md')
    assert 'description: "Completion Check: Verify Infrastructure Is Wired"' in text, "expected to find: " + 'description: "Completion Check: Verify Infrastructure Is Wired"'[:80]

