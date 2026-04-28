"""Behavioral checks for ruby-sdk-add-agentsmd-with-comprehensive-development (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruby-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/release-changelogs.mdc')
    assert '.cursor/rules/release-changelogs.mdc' in text, "expected to find: " + '.cursor/rules/release-changelogs.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the official Ruby SDK for the Model Context Protocol (MCP), implementing both server and client functionality for JSON-RPC 2.0 based communication between LLM applications and context provider' in text, "expected to find: " + 'This is the official Ruby SDK for the Model Context Protocol (MCP), implementing both server and client functionality for JSON-RPC 2.0 based communication between LLM applications and context provider'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Implements MCP protocol methods: initialize, ping, tools/list, tools/call, prompts/list, prompts/get, resources/list, resources/read' in text, "expected to find: " + '- Implements MCP protocol methods: initialize, ping, tools/list, tools/call, prompts/list, prompts/get, resources/list, resources/read'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Protocol version 2025-03-26+ supports tool annotations (destructive_hint, idempotent_hint, etc.)' in text, "expected to find: " + '- Protocol version 2025-03-26+ supports tool annotations (destructive_hint, idempotent_hint, etc.)'[:80]

