"""Behavioral checks for skills-docs-revamp-agentsmd-with-karpathyinspired (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Agent Skills is a repository of skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry services.' in text, "expected to find: " + 'Agent Skills is a repository of skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry services.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Usage:** MCPs are available when configured in your editor. Use `microsoft-docs` to search official documentation before implementing Azure SDK code.' in text, "expected to find: " + '**Usage:** MCPs are available when configured in your editor. Use `microsoft-docs` to search official documentation before implementing Azure SDK code.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Search official docs first** — Use the Microsoft Docs MCP (`microsoft-docs`) to get current API signatures, parameters, and patterns' in text, "expected to find: " + '1. **Search official docs first** — Use the Microsoft Docs MCP (`microsoft-docs`) to get current API signatures, parameters, and patterns'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '**Usage:** MCPs are available when configured in your editor. Use `microsoft-docs` to search official documentation before implementing Azure SDK code.' in text, "expected to find: " + '**Usage:** MCPs are available when configured in your editor. Use `microsoft-docs` to search official documentation before implementing Azure SDK code.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '1. **Search official docs first** — Use the Microsoft Docs MCP (`microsoft-docs`) to get current API signatures, parameters, and patterns' in text, "expected to find: " + '1. **Search official docs first** — Use the Microsoft Docs MCP (`microsoft-docs`) to get current API signatures, parameters, and patterns'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert 'A repository of skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry services.' in text, "expected to find: " + 'A repository of skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry services.'[:80]

