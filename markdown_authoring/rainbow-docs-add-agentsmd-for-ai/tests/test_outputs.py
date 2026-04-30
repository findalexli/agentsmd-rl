"""Behavioral checks for rainbow-docs-add-agentsmd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rainbow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '@../AGENTS.md' in text, "expected to find: " + '@../AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Stores live in `src/state/` (one per domain) and in `src/features/*/data/stores/`. These in-repo creators are being replaced by the external [`stores`](https://github.com/christianbaroni/stores) packa' in text, "expected to find: " + 'Stores live in `src/state/` (one per domain) and in `src/features/*/data/stores/`. These in-repo creators are being replaced by the external [`stores`](https://github.com/christianbaroni/stores) packa'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The codebase is mid-migration toward domain-organized architecture. New code goes in `src/features/` with `ui/data/core` layer separation. Legacy code lives in flat top-level directories (`components/' in text, "expected to find: " + 'The codebase is mid-migration toward domain-organized architecture. New code goes in `src/features/` with `ui/data/core` layer separation. Legacy code lives in flat top-level directories (`components/'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`createQueryStore`** -- combines data fetching + state in one store. Reactive `$` params auto-refetch when dependencies change. Replaces the React Query + Zustand dual-store pattern. Use for serve' in text, "expected to find: " + '- **`createQueryStore`** -- combines data fetching + state in one store. Reactive `$` params auto-refetch when dependencies change. Replaces the React Query + Zustand dual-store pattern. Use for serve'[:80]

