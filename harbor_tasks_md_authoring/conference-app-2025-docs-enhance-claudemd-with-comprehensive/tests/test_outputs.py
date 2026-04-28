"""Behavioral checks for conference-app-2025-docs-enhance-claudemd-with-comprehensive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/conference-app-2025")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is a Kotlin Multiplatform (KMP) conference application supporting Android, iOS, and Desktop platforms with sophisticated architecture patterns:' in text, "expected to find: " + 'This is a Kotlin Multiplatform (KMP) conference application supporting Android, iOS, and Desktop platforms with sophisticated architecture patterns:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is the **DroidKaigi 2025 conference application** - a Kotlin Multiplatform project supporting Android, iOS, and Desktop platforms.' in text, "expected to find: " + 'This is the **DroidKaigi 2025 conference application** - a Kotlin Multiplatform project supporting Android, iOS, and Desktop platforms.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Replaces traditional repository pattern with [Soil](https://github.com/soil-kt/soil) for composable-first data fetching' in text, "expected to find: " + '- Replaces traditional repository pattern with [Soil](https://github.com/soil-kt/soil) for composable-first data fetching'[:80]

