"""Behavioral checks for cc-wf-studio-chore-simplify-redundant-biome-commands (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cc-wf-studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'npm run check   # Run all Biome checks (lint + format, with auto-fix)' in text, "expected to find: " + 'npm run check   # Run all Biome checks (lint + format, with auto-fix)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Runs lint + format with auto-fix in a single command' in text, "expected to find: " + '- Runs lint + format with auto-fix in a single command'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'npm run check' in text, "expected to find: " + 'npm run check'[:80]

