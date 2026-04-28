"""Behavioral checks for spiceai-docs-update-error-handling-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spiceai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **NO `.unwrap()` in test code**: All Result unwraps that are not handled with `?` in tests should use `.expect()` with a sensible message instead' in text, "expected to find: " + '- **NO `.unwrap()` in test code**: All Result unwraps that are not handled with `?` in tests should use `.expect()` with a sensible message instead'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Note**: In test code, `.expect()` with descriptive messages is preferred over `.unwrap()` since test failures should panic with clear context.' in text, "expected to find: " + '**Note**: In test code, `.expect()` with descriptive messages is preferred over `.unwrap()` since test failures should panic with clear context.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **NO `.unwrap()` or `.expect()` in non-test code**: Use proper error handling with `?` operator or `match`' in text, "expected to find: " + '- **NO `.unwrap()` or `.expect()` in non-test code**: Use proper error handling with `?` operator or `match`'[:80]

