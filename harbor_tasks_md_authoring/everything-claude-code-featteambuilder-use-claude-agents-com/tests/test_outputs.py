"""Behavioral checks for everything-claude-code-featteambuilder-use-claude-agents-com (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/team-builder/SKILL.md')
    assert '1. **`claude agents` command** (primary) — run `claude agents` to get all agents known to the CLI, including user agents, plugin agents (e.g. `everything-claude-code:architect`), and built-in agents. ' in text, "expected to find: " + '1. **`claude agents` command** (primary) — run `claude agents` to get all agents known to the CLI, including user agents, plugin agents (e.g. `everything-claude-code:architect`), and built-in agents. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/team-builder/SKILL.md')
    assert '- **Plugin agents** are prefixed with `plugin-name:` (e.g., `everything-claude-code:security-reviewer`). Use the part after `:` as the agent name and the plugin name as the domain.' in text, "expected to find: " + '- **Plugin agents** are prefixed with `plugin-name:` (e.g., `everything-claude-code:security-reviewer`). Use the part after `:` as the agent name and the plugin name as the domain.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/team-builder/SKILL.md')
    assert 'If no agents are found after running `claude agents` and probing file locations, inform the user: "No agents found. Run `claude agents` to verify your setup." Then stop.' in text, "expected to find: " + 'If no agents are found after running `claude agents` and probing file locations, inform the user: "No agents found. Run `claude agents` to verify your setup." Then stop.'[:80]

