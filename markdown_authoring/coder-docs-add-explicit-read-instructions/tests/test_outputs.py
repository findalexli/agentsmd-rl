"""Behavioral checks for coder-docs-add-explicit-read-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/coder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.claude/docs/ARCHITECTURE.md` — system overview (orientation or architecture work)' in text, "expected to find: " + '- `.claude/docs/ARCHITECTURE.md` — system overview (orientation or architecture work)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.claude/docs/TESTING.md` — testing patterns, race conditions (any test changes)' in text, "expected to find: " + '- `.claude/docs/TESTING.md` — testing patterns, race conditions (any test changes)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.claude/docs/DOCS_STYLE_GUIDE.md` — docs conventions (when writing `docs/`)' in text, "expected to find: " + '- `.claude/docs/DOCS_STYLE_GUIDE.md` — docs conventions (when writing `docs/`)'[:80]

