"""Behavioral checks for onlook-docsagents-tighten-wording-remove-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/onlook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Create store instances with `useState(() => new Store())` for stability across' in text, "expected to find: " + '- Create store instances with `useState(() => new Store())` for stability across'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Avoid `useMemo` for store instances; React may drop memoized values leading to' in text, "expected to find: " + '- Avoid `useMemo` for store instances; React may drop memoized values leading to'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Example store: `apps/web/client/src/components/store/editor/engine.ts:1` (uses' in text, "expected to find: " + '- Example store: `apps/web/client/src/components/store/editor/engine.ts:1` (uses'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

