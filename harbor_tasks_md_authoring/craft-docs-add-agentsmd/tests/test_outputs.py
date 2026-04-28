"""Behavioral checks for craft-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/craft")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Prettier** with single quotes and no arrow parens (configured in `.prettierrc.yml`).' in text, "expected to find: " + '- **Prettier** with single quotes and no arrow parens (configured in `.prettierrc.yml`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Test files are located in `src/__tests__/` and follow the `*.test.ts` naming pattern.' in text, "expected to find: " + '- Test files are located in `src/__tests__/` and follow the `*.test.ts` naming pattern.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides guidance for AI coding assistants working with the Craft codebase.' in text, "expected to find: " + 'This file provides guidance for AI coding assistants working with the Craft codebase.'[:80]

