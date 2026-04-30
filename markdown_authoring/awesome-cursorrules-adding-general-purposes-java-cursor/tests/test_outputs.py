"""Behavioral checks for awesome-cursorrules-adding-general-purposes-java-cursor (markdown_authoring task).

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
    text = _read('rules/java-general-purpose-cursorrules-prompt-file/.cursorrules')
    assert '- "Use checked exceptions for recoverable conditions and runtime exceptions for programming errors"' in text, "expected to find: " + '- "Use checked exceptions for recoverable conditions and runtime exceptions for programming errors"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/java-general-purpose-cursorrules-prompt-file/.cursorrules')
    assert '- "Enforce the singleton property with a private constructor or an enum type"' in text, "expected to find: " + '- "Enforce the singleton property with a private constructor or an enum type"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/java-general-purpose-cursorrules-prompt-file/.cursorrules')
    assert '- "Consider a builder when faced with many constructor parameters"' in text, "expected to find: " + '- "Consider a builder when faced with many constructor parameters"'[:80]

