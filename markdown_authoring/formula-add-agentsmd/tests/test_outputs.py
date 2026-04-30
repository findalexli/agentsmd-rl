"""Behavioral checks for formula-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/formula")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `ActionFormula<Input, Output>` - converts Action to Formula, emits initialValue until action produces value. Resubscribes on input change.' in text, "expected to find: " + '- `ActionFormula<Input, Output>` - converts Action to Formula, emits initialValue until action produces value. Resubscribes on input change.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Result types: `Stateful(state, effects)` (new state + optional effects), `OnlyEffects(effects)` (no state change), `None` (nothing).' in text, "expected to find: " + '- Result types: `Stateful(state, effects)` (new state + optional effects), `OnlyEffects(effects)` (no state change), `None` (nothing).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `Input` - Immutable data from parent containing data and event listeners. Changes trigger re-evaluation. Use `Unit` if none needed.' in text, "expected to find: " + '- `Input` - Immutable data from parent containing data and event listeners. Changes trigger re-evaluation. Use `Unit` if none needed.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

