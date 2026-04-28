"""Behavioral checks for inspector-move-agent-instructions-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/inspector")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `cli/`: Command-line interface for testing and invoking MCP server methods directly' in text, "expected to find: " + '- `cli/`: Command-line interface for testing and invoking MCP server methods directly'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Development mode: `npm run dev` (use `npm run dev:windows` on Windows)' in text, "expected to find: " + '- Development mode: `npm run dev` (use `npm run dev:windows` on Windows)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep components small and focused on a single responsibility' in text, "expected to find: " + '- Keep components small and focused on a single responsibility'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '@./AGENTS.md' in text, "expected to find: " + '@./AGENTS.md'[:80]

