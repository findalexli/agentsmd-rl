"""Behavioral checks for automat-claudemd-forbid-subagents-for-codebase (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/automat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Do not use sub-agents (Agent / Task / Explore) for codebase exploration.** Read the actual source files yourself with Read/Grep/Glob. Sub-agent summaries are lossy and have introduced factual erro' in text, "expected to find: " + '- **Do not use sub-agents (Agent / Task / Explore) for codebase exploration.** Read the actual source files yourself with Read/Grep/Glob. Sub-agent summaries are lossy and have introduced factual erro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- The authoritative list of process-wide state lives in `src/automat.hh` and `src/root_widget.hh`. Init and teardown order is explicit in `automat::Main()` in `src/automat.cc`.' in text, "expected to find: " + '- The authoritative list of process-wide state lives in `src/automat.hh` and `src/root_widget.hh`. Init and teardown order is explicit in `automat::Main()` in `src/automat.cc`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '## Working in this codebase' in text, "expected to find: " + '## Working in this codebase'[:80]

