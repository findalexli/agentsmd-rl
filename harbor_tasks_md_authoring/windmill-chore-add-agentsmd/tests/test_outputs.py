"""Behavioral checks for windmill-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/windmill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**MUST use `outline` before `Read`** on unfamiliar files — a 500-line file costs ~500 lines of context, while `outline` costs ~20. Then **MUST use `body "X"`** instead of reading a full file to see on' in text, "expected to find: " + '**MUST use `outline` before `Read`** on unfamiliar files — a 500-line file costs ~500 lines of context, while `outline` costs ~20. Then **MUST use `body "X"`** instead of reading a full file to see on'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Understand**: Before coding, explore the codebase (see Code Navigation below). Use `outline` to understand file structure, `body` to read specific symbols, `def`/`callers`/`callees` to trace code' in text, "expected to find: " + '1. **Understand**: Before coding, explore the codebase (see Code Navigation below). Use `outline` to understand file structure, `body` to read specific symbols, `def`/`callers`/`callees` to trace code'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Create a `useMyPropState()` helper** — encapsulate the undefined-handling logic in a reusable function and call it higher in the component tree, so the child component always receives a defined v' in text, "expected to find: " + '2. **Create a `useMyPropState()` helper** — encapsulate the undefined-handling logic in a reusable function and call it higher in the component tree, so the child component always receives a defined v'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

