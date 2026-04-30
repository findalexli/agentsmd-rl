"""Behavioral checks for prql-docs-add-pointer-to-developmentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`web/book/src/project/contributing/development.md`.' in text, "expected to find: " + '`web/book/src/project/contributing/development.md`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For releases or environment issues, see' in text, "expected to find: " + 'For releases or environment issues, see'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '## Releases & Environment' in text, "expected to find: " + '## Releases & Environment'[:80]

