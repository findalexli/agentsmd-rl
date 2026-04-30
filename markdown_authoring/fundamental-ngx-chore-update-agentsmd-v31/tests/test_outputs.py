"""Behavioral checks for fundamental-ngx-chore-update-agentsmd-v31 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fundamental-ngx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "When migrating from `@Input()` decorators to `input()` signals, you may encounter cases where external code needs to programmatically update a directive's input value. **Signal inputs are read-only** " in text, "expected to find: " + "When migrating from `@Input()` decorators to `input()` signals, you may encounter cases where external code needs to programmatically update a directive's input value. **Signal inputs are read-only** "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `Subject<void>` for notifications         | Replace with `effect()` on signal        | [Effect vs Observables](#effect-vs-observables)                                    |' in text, "expected to find: " + '| `Subject<void>` for notifications         | Replace with `effect()` on signal        | [Effect vs Observables](#effect-vs-observables)                                    |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `contentChild()` returns undefined        | Use `?? null` for null-expecting signals | [Queries](#queries)                                                                |' in text, "expected to find: " + '| `contentChild()` returns undefined        | Use `?? null` for null-expecting signals | [Queries](#queries)                                                                |'[:80]

