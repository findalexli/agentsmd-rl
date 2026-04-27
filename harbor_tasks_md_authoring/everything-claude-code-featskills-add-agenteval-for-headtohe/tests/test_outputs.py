"""Behavioral checks for everything-claude-code-featskills-add-agenteval-for-headtohe (markdown_authoring task).

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
    text = _read('skills/agent-eval/SKILL.md')
    assert 'A lightweight CLI tool for comparing coding agents head-to-head on reproducible tasks. Every "which coding agent is best?" comparison runs on vibes — this tool systematizes it.' in text, "expected to find: " + 'A lightweight CLI tool for comparing coding agents head-to-head on reproducible tasks. Every "which coding agent is best?" comparison runs on vibes — this tool systematizes it.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-eval/SKILL.md')
    assert 'Each agent run gets its own git worktree — no Docker required. This provides reproducibility isolation so agents cannot interfere with each other or corrupt the base repo.' in text, "expected to find: " + 'Each agent run gets its own git worktree — no Docker required. This provides reproducibility isolation so agents cannot interfere with each other or corrupt the base repo.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-eval/SKILL.md')
    assert 'description: Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics' in text, "expected to find: " + 'description: Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics'[:80]

