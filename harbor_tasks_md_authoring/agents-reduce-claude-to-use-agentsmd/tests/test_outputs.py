"""Behavioral checks for agents-reduce-claude-to-use-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert 'This is the **Inkeep Agent Framework** - a multi-agent AI system with A2A (Agent-to-Agent) communication capabilities. The system provides OpenAI Chat Completions compatible API while supporting sophi' in text, "expected to find: " + 'This is the **Inkeep Agent Framework** - a multi-agent AI system with A2A (Agent-to-Agent) communication capabilities. The system provides OpenAI Chat Completions compatible API while supporting sophi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '- **Context Extraction**: For delegation scenarios, extract contextId from task ID patterns like `task_math-demo-123456-chatcmpl-789`' in text, "expected to find: " + '- **Context Extraction**: For delegation scenarios, extract contextId from task ID patterns like `task_math-demo-123456-chatcmpl-789`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert 'This file provides guidance for AI coding agents (Claude Code, Cursor, Codex, Amp, etc.) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance for AI coding agents (Claude Code, Cursor, Codex, Amp, etc.) when working with code in this repository.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'AGENTS.md follows the emerging standard for AI coding agent guidance files, making this repository compatible with multiple AI coding assistants (Claude Code, Cursor, Codex, Amp, and others). See [age' in text, "expected to find: " + 'AGENTS.md follows the emerging standard for AI coding agent guidance files, making this repository compatible with multiple AI coding assistants (Claude Code, Cursor, Codex, Amp, and others). See [age'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository uses **AGENTS.md** as the primary guide for AI coding agents.' in text, "expected to find: " + 'This repository uses **AGENTS.md** as the primary guide for AI coding agents.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Please refer to [AGENTS.md](./AGENTS.md) for comprehensive documentation.**' in text, "expected to find: " + '**Please refer to [AGENTS.md](./AGENTS.md) for comprehensive documentation.**'[:80]

