"""Behavioral checks for awesome-cursorrules-enhance-unity-tower-defense-game (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules')
    assert '// The project is currently undergoing refactoring for better extensibility and maintainability.' in text, "expected to find: " + '// The project is currently undergoing refactoring for better extensibility and maintainability.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules')
    assert '// This project involves creating a tower defense style game controlled by a Nintendo Ringcon.' in text, "expected to find: " + '// This project involves creating a tower defense style game controlled by a Nintendo Ringcon.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/unity-cursor-ai-c-cursorrules-prompt-file/.cursorrules')
    assert '// Feel free to ask questions if you need more information about the project intentions.' in text, "expected to find: " + '// Feel free to ask questions if you need more information about the project intentions.'[:80]

