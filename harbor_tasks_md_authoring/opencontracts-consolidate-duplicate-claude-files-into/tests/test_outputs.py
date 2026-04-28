"""Behavioral checks for opencontracts-consolidate-duplicate-claude-files-into (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencontracts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Both read from Apollo reactive vars (`showStructuralAnnotations`, `showSelectedAnnotationOnly` in `cache.ts`)' in text, "expected to find: " + '- Both read from Apollo reactive vars (`showStructuralAnnotations`, `showSelectedAnnotationOnly` in `cache.ts`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Claude.md')
    assert 'Claude.md' in text, "expected to find: " + 'Claude.md'[:80]

