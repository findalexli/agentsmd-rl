"""Behavioral checks for awesome-cursorrules-cursorrules-for-flutter-with-riverpod (markdown_authoring task).

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
    text = _read('rules/flutter-riverpod-cursorrules-prompt-file/.cursorrules')
    assert 'This document outlines the placement rules for files and folders within the recommended Flutter project structure, focusing on scalability, maintainability, and adherence to Clean Architecture princip' in text, "expected to find: " + 'This document outlines the placement rules for files and folders within the recommended Flutter project structure, focusing on scalability, maintainability, and adherence to Clean Architecture princip'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/flutter-riverpod-cursorrules-prompt-file/.cursorrules')
    assert '- **Do not arbitrarily change versions listed in the tech stack** (APIs, frameworks, libraries, etc.). If changes are necessary, clearly explain the reason and wait for approval before making any chan' in text, "expected to find: " + '- **Do not arbitrarily change versions listed in the tech stack** (APIs, frameworks, libraries, etc.). If changes are necessary, clearly explain the reason and wait for approval before making any chan'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/flutter-riverpod-cursorrules-prompt-file/.cursorrules')
    assert '- **Do not make changes that are not explicitly instructed.** If changes seem necessary, first report them as proposals and implement only after approval' in text, "expected to find: " + '- **Do not make changes that are not explicitly instructed.** If changes seem necessary, first report them as proposals and implement only after approval'[:80]

