"""Behavioral checks for docker-agent-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docker-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Agent properties**: name, model, description, instruction, sub_agents, toolsets, add_date, add_environment_info, code_mode_tools, max_iterations, num_history_items' in text, "expected to find: " + '- **Agent properties**: name, model, description, instruction, sub_agents, toolsets, add_date, add_environment_info, code_mode_tools, max_iterations, num_history_items'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Tool configuration**: MCP tools (local stdio and remote), builtin tools (filesystem, shell, think, todo, memory, etc.)' in text, "expected to find: " + '- **Tool configuration**: MCP tools (local stdio and remote), builtin tools (filesystem, shell, think, todo, memory, etc.)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Docker-based MCP**: Reference MCP servers from Docker images (e.g., `docker:github-official`)' in text, "expected to find: " + '- **Docker-based MCP**: Reference MCP servers from Docker images (e.g., `docker:github-official`)'[:80]

