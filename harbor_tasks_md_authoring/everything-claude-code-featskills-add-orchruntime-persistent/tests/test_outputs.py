"""Behavioral checks for everything-claude-code-featskills-add-orchruntime-persistent (markdown_authoring task).

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
    text = _read('skills/orch-runtime/SKILL.md')
    assert 'Use this skill when you need to hand off work to a **persistent, stateful AI agent team** managed by ORCH — the TypeScript CLI runtime for coordinating Claude Code, OpenCode, Codex, and Cursor agents.' in text, "expected to find: " + 'Use this skill when you need to hand off work to a **persistent, stateful AI agent team** managed by ORCH — the TypeScript CLI runtime for coordinating Claude Code, OpenCode, Codex, and Cursor agents.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orch-runtime/SKILL.md')
    assert 'description: Dispatch tasks to a persistent ORCH agent team from Claude Code. Use when you need long-running or multi-session AI workflows that survive beyond a single Claude context window.' in text, "expected to find: " + 'description: Dispatch tasks to a persistent ORCH agent team from Claude Code. Use when you need long-running or multi-session AI workflows that survive beyond a single Claude context window.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orch-runtime/SKILL.md')
    assert "ORCH's orchestrator tick loop detects zombie processes and stalled tasks. If an agent exceeds `stall_timeout_ms`, the task is retried or failed automatically." in text, "expected to find: " + "ORCH's orchestrator tick loop detects zombie processes and stalled tasks. If an agent exceeds `stall_timeout_ms`, the task is retried or failed automatically."[:80]

