"""Behavioral checks for persistent-agent-runtime-docs-consolidate-claudemd-into-agen (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/persistent-agent-runtime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Non-negotiable when installed.** At conversation start, invoke `using-superpowers` via the `Skill` tool before any other action — including reading files or asking clarifying questions. Before every' in text, "expected to find: " + '**Non-negotiable when installed.** At conversation start, invoke `using-superpowers` via the `Skill` tool before any other action — including reading files or asking clarifying questions. Before every'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Verify with Playwright MCP tools against `make start` (Console at `localhost:5173`, API at `localhost:8080`). Run Scenario 1 (Navigation Smoke Test) plus the feature scenario covering your change. If ' in text, "expected to find: " + 'Verify with Playwright MCP tools against `make start` (Console at `localhost:5173`, API at `localhost:8080`). Run Scenario 1 (Navigation Smoke Test) plus the feature scenario covering your change. If '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When a phase exceeds ~40 tasks, split into sequential tracks of ~7-10 tasks each. Tracks are spec subsections, may add `track-N-<name>.md` design docs, and each get their own `exec-plans/` subdirector' in text, "expected to find: " + 'When a phase exceeds ~40 tasks, split into sequential tracks of ~7-10 tasks each. Tracks are spec subsections, may add `track-N-<name>.md` design docs, and each get their own `exec-plans/` subdirector'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

