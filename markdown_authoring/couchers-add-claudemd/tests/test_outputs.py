"""Behavioral checks for couchers-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/couchers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- NEVER try-catch an exception and silently throw it away or just log it. By and large you don't need to wrap code in try-catch blocks, we already handle exceptions" in text, "expected to find: " + "- NEVER try-catch an exception and silently throw it away or just log it. By and large you don't need to wrap code in try-catch blocks, we already handle exceptions"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Imports always occur at the top of the file. The two exceptions are when this is required during type checking or in tests that really require inline imports' in text, "expected to find: " + '- Imports always occur at the top of the file. The two exceptions are when this is required during type checking or in tests that really require inline imports'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use `enum.auto()` for all enums (except in the rare case that they are inherently ordinal and we use that order in business logic)' in text, "expected to find: " + '- Use `enum.auto()` for all enums (except in the rare case that they are inherently ordinal and we use that order in business logic)'[:80]

