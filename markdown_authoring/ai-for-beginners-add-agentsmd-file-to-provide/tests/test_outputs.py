"""Behavioral checks for ai-for-beginners-add-agentsmd-file-to-provide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AI for Beginners is a comprehensive 12-week, 24-lesson curriculum covering Artificial Intelligence fundamentals. This educational repository includes practical lessons using Jupyter Notebooks, quizzes' in text, "expected to find: " + 'AI for Beginners is a comprehensive 12-week, 24-lesson curriculum covering Artificial Intelligence fundamentals. This educational repository includes practical lessons using Jupyter Notebooks, quizzes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Architecture:** Educational content repository with Jupyter Notebooks organized by topic areas, supplemented by a Vue.js-based quiz application and extensive multi-language support.' in text, "expected to find: " + '**Architecture:** Educational content repository with Jupyter Notebooks organized by topic areas, supplemented by a Vue.js-based quiz application and extensive multi-language support.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is an educational repository focused on learning content rather than software testing. There is no traditional test suite.' in text, "expected to find: " + 'This is an educational repository focused on learning content rather than software testing. There is no traditional test suite.'[:80]

