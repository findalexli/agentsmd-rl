"""Behavioral checks for liam-docs-move-database-operations-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/liam")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious' in text, "expected to find: " + '- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Delete fearlessly, Git remembers** – Cut dead code, stale logic, and verbose history' in text, "expected to find: " + '- **Delete fearlessly, Git remembers** – Cut dead code, stale logic, and verbose history'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/internal-packages/db/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with database operations.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with database operations.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/internal-packages/db/CLAUDE.md')
    assert 'For database migration and type generation workflows, see @../../../docs/migrationOpsContext.md' in text, "expected to find: " + 'For database migration and type generation workflows, see @../../../docs/migrationOpsContext.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/internal-packages/db/CLAUDE.md')
    assert '# CLAUDE.md - Database Package' in text, "expected to find: " + '# CLAUDE.md - Database Package'[:80]

