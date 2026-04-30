"""Behavioral checks for wvlet-doc-reorganize-git-and-development (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wvlet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Gemini will review pull requests for code quality, adherence to guidelines, and test coverage. Reflect on feedback and make necessary changes' in text, "expected to find: " + '- Gemini will review pull requests for code quality, adherence to guidelines, and test coverage. Reflect on feedback and make necessary changes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- After creating a PR, wait for review from Gemini for a while, and reflect on the suggestions, and update the PR' in text, "expected to find: " + '- After creating a PR, wait for review from Gemini for a while, and reflect on the suggestions, and update the PR'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- If modifying project structure, development processes, or adding new guidelines, update this file' in text, "expected to find: " + '- If modifying project structure, development processes, or adding new guidelines, update this file'[:80]

