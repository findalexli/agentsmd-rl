"""Behavioral checks for avoid-ai-writing-expand-aiism-coverage-new-words (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/avoid-ai-writing")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- "Let\'s explore," "Let\'s take a look," "Let\'s break this down," "Let\'s examine" — AI uses "let\'s" as a false-collaborative opener to ease into a topic. It\'s filler that delays the actual point. Just ' in text, "expected to find: " + '- "Let\'s explore," "Let\'s take a look," "Let\'s break this down," "Let\'s examine" — AI uses "let\'s" as a false-collaborative opener to ease into a topic. It\'s filler that delays the actual point. Just '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- Note: "In order to," "Due to the fact that," and "At the end of the day" are covered in the word/phrase table and transition sections above — don\'t duplicate rules.' in text, "expected to find: " + '- Note: "In order to," "Due to the fact that," and "At the end of the day" are covered in the word/phrase table and transition sections above — don\'t duplicate rules.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| revolutionize | change, transform, reshape (or describe what changed) |' in text, "expected to find: " + '| revolutionize | change, transform, reshape (or describe what changed) |'[:80]

