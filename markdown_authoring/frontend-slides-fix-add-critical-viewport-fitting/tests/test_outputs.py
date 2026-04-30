"""Behavioral checks for frontend-slides-fix-add-critical-viewport-fitting (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/frontend-slides")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **When adding images to existing slides:** Move image to new slide or reduce other content first' in text, "expected to find: " + '- **When adding images to existing slides:** Move image to new slide or reduce other content first'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- If adding content exceeds limits → **Split into multiple slides or create a continuation slide**' in text, "expected to find: " + '- If adding content exceeds limits → **Split into multiple slides or create a continuation slide**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- Inform user: "I\'ve reorganized the content across 2 slides to ensure proper viewport fitting"' in text, "expected to find: " + '- Inform user: "I\'ve reorganized the content across 2 slides to ensure proper viewport fitting"'[:80]

