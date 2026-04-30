"""Behavioral checks for anytype-swift-updated-claudemd (markdown_authoring task).

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
    assert 'After making code changes, report them to the user who will verify compilation in Xcode (faster with caches).' in text, "expected to find: " + 'After making code changes, report them to the user who will verify compilation in Xcode (faster with caches).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. Report changes to user for compilation verification' in text, "expected to find: " + '3. Report changes to user for compilation verification'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '### Compilation Verification' in text, "expected to find: " + '### Compilation Verification'[:80]

