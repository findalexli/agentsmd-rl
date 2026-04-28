"""Behavioral checks for kelos-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kelos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **For CI/release workflows**, always use existing Makefile targets rather than reimplementing build logic in YAML.' in text, "expected to find: " + '- **For CI/release workflows**, always use existing Makefile targets rather than reimplementing build logic in YAML.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Keep changes minimal.** Do not refactor, reorganize, or 'improve' code beyond what was explicitly requested." in text, "expected to find: " + "- **Keep changes minimal.** Do not refactor, reorganize, or 'improve' code beyond what was explicitly requested."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Better tests** Always try to add or improve tests(including integration, e2e) when modifying code.' in text, "expected to find: " + '- **Better tests** Always try to add or improve tests(including integration, e2e) when modifying code.'[:80]

