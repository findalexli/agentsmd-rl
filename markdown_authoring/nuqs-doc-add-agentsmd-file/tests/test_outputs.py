"""Behavioral checks for nuqs-doc-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nuqs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Batch + throttle: multiple `setState` calls in one tick are merged; URL updates throttled (≥50ms unless overridden).' in text, "expected to find: " + '- Batch + throttle: multiple `setState` calls in one tick are merged; URL updates throttled (≥50ms unless overridden).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `throttleMs`: ≥50ms (ignored if lower). Only URL & server notification are throttled, not in-memory state.' in text, "expected to find: " + '- `throttleMs`: ≥50ms (ignored if lower). Only URL & server notification are throttled, not in-memory state.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'API testing: check exported symbols in `packages/nuqs/src/api.test.ts` => update when exporting new symbols' in text, "expected to find: " + 'API testing: check exported symbols in `packages/nuqs/src/api.test.ts` => update when exporting new symbols'[:80]

