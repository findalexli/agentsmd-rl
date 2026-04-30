"""Behavioral checks for mux-docs-add-pr-title-structure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mux")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- **perf:** (improvement to performance, no functionality changes)' in text, "expected to find: " + '- **perf:** (improvement to performance, no functionality changes)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- **refactor:** (improvement to codebase, no behavior changes)' in text, "expected to find: " + '- **refactor:** (improvement to codebase, no behavior changes)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- `🤖 perf: cache markdown plugin arrays to avoid re-parsing`' in text, "expected to find: " + '- `🤖 perf: cache markdown plugin arrays to avoid re-parsing`'[:80]

