"""Behavioral checks for claude-code-statusline-chore-update-claudemd-for-v2190 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-statusline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Data Flow**: JSON input → Config loading → Theme application → Atomic component data collection → 1-9 line dynamic output (default: 9-line with wellness + GPS location)' in text, "expected to find: " + '**Data Flow**: JSON input → Config loading → Theme application → Atomic component data collection → 1-9 line dynamic output (default: 9-line with wellness + GPS location)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Core Modules** (14): core → security → config → themes → cache → git → mcp → cost → prayer → wellness → focus → components → display' in text, "expected to find: " + '**Core Modules** (14): core → security → config → themes → cache → git → mcp → cost → prayer → wellness → focus → components → display'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Features**: 9-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location, wellness, CLI analytics' in text, "expected to find: " + '**Features**: 9-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location, wellness, CLI analytics'[:80]

