"""Behavioral checks for everything-claude-code-docs-add-claudemd-for-claude (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert 'This is a **Claude Code plugin** - a collection of production-ready agents, skills, hooks, commands, rules, and MCP configurations. The project provides battle-tested workflows for software developmen' in text, "expected to find: " + 'This is a **Claude Code plugin** - a collection of production-ready agents, skills, hooks, commands, rules, and MCP configurations. The project provides battle-tested workflows for software developmen'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Package manager detection: npm, pnpm, yarn, bun (configurable via `CLAUDE_PACKAGE_MANAGER` env var or project config)' in text, "expected to find: " + '- Package manager detection: npm, pnpm, yarn, bun (configurable via `CLAUDE_PACKAGE_MANAGER` env var or project config)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]

