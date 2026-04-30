"""Behavioral checks for flow-playground-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flow-playground")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Styling: Theme UI theme values first, then `@emotion`.** Prefer values from `src/theme.ts`;' in text, "expected to find: " + '- **Styling: Theme UI theme values first, then `@emotion`.** Prefer values from `src/theme.ts`;'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'others) when working in this repository. It is loaded into agent context automatically — keep' in text, "expected to find: " + 'others) when working in this repository. It is loaded into agent context automatically — keep'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Node 18.x is required (`package.json` `engines.node`). Use `npm` — `package-lock.json` is the' in text, "expected to find: " + 'Node 18.x is required (`package.json` `engines.node`). Use `npm` — `package-lock.json` is the'[:80]

