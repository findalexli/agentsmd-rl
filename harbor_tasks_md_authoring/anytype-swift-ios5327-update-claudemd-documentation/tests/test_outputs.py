"""Behavioral checks for anytype-swift-ios5327-update-claudemd-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anytype-swift")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Remove unused code after refactoring** - Delete unused properties, functions, and entire files that are no longer referenced' in text, "expected to find: " + '- **Remove unused code after refactoring** - Delete unused properties, functions, and entire files that are no longer referenced'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Identify the task branch**: The branch name follows the format `ios-XXXX-description`' in text, "expected to find: " + '1. **Identify the task branch**: The branch name follows the format `ios-XXXX-description`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Switch to the task branch IMMEDIATELY** before doing ANY other work:' in text, "expected to find: " + '2. **Switch to the task branch IMMEDIATELY** before doing ANY other work:'[:80]

