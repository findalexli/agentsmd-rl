"""Behavioral checks for shardingsphere-enhance-claudemd-with-codeofconductmd-integra (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shardingsphere")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. Follow CODE_OF_CONDUCT.md (clean code principles, naming conventions, formatting)' in text, "expected to find: " + '1. Follow CODE_OF_CONDUCT.md (clean code principles, naming conventions, formatting)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)' in text, "expected to find: " + '1. Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- No redundant test cases - each test validates unique behavior' in text, "expected to find: " + '- No redundant test cases - each test validates unique behavior'[:80]

