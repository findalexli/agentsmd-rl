"""Behavioral checks for cursorless-claudemd-imports-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursorless")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For versatile actions like `drink`, `pour`, `drop`, `float`, and `puff`, explain their behavior with different scope types' in text, "expected to find: " + '- For versatile actions like `drink`, `pour`, `drop`, `float`, and `puff`, explain their behavior with different scope types'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Contributing documentation is in `/packages/cursorless-org-docs/src/docs/contributing/`' in text, "expected to find: " + '- Contributing documentation is in `/packages/cursorless-org-docs/src/docs/contributing/`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Main documentation is in `/packages/cursorless-org-docs/src/docs/user/README.md`' in text, "expected to find: " + '- Main documentation is in `/packages/cursorless-org-docs/src/docs/user/README.md`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

