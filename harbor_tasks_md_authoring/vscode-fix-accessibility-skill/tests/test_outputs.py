"""Behavioral checks for vscode-fix-accessibility-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/accessibility/SKILL.md')
    assert 'description: Accessibility guidelines for VS Code features — covers accessibility help dialogs, accessible views, verbosity settings, accessibility signals, ARIA alerts/status announcements, keyboard ' in text, "expected to find: " + 'description: Accessibility guidelines for VS Code features — covers accessibility help dialogs, accessible views, verbosity settings, accessibility signals, ARIA alerts/status announcements, keyboard '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/accessibility/SKILL.md')
    assert 'name: accessibility' in text, "expected to find: " + 'name: accessibility'[:80]

