"""Behavioral checks for nanoclaw-skilladdgcaltool-oneclinative-google-calendar-mcp (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gcal-tool/SKILL.md')
    assert 'This skill wires [`@cocal/google-calendar-mcp`](https://github.com/cocal-com/google-calendar-mcp) into selected agent groups. The MCP server reads stub credentials containing the `onecli-managed` plac' in text, "expected to find: " + 'This skill wires [`@cocal/google-calendar-mcp`](https://github.com/cocal-com/google-calendar-mcp) into selected agent groups. The MCP server reads stub credentials containing the `onecli-managed` plac'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gcal-tool/SKILL.md')
    assert 'Tools exposed (surfaced as `mcp__calendar__<name>`, exact set depends on version — run `tools/list` against the MCP server to enumerate): `list-calendars`, `list-events`, `search-events`, `create-even' in text, "expected to find: " + 'Tools exposed (surfaced as `mcp__calendar__<name>`, exact set depends on version — run `tools/list` against the MCP server to enumerate): `list-calendars`, `list-events`, `search-events`, `create-even'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gcal-tool/SKILL.md')
    assert 'description: Add Google Calendar as an MCP tool (list calendars, list/search/create events, free/busy queries) using OneCLI-managed OAuth. Multi-calendar and multi-account supported. Mirrors /add-gmai' in text, "expected to find: " + 'description: Add Google Calendar as an MCP tool (list calendars, list/search/create events, free/busy queries) using OneCLI-managed OAuth. Multi-calendar and multi-account supported. Mirrors /add-gmai'[:80]

