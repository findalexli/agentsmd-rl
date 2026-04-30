"""Behavioral checks for autoresearch-docs-add-agentsmd-for-universal (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autoresearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Autonomous goal-directed iteration based on [Karpathy's autoresearch](https://github.com/karpathy/autoresearch). One metric, constrained scope, fast verification, automatic rollback, git as memory. Wo" in text, "expected to find: " + "Autonomous goal-directed iteration based on [Karpathy's autoresearch](https://github.com/karpathy/autoresearch). One metric, constrained scope, fast verification, automatic rollback, git as memory. Wo"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> Drop this file into your project root. Any AI agent (Claude Code, Codex, OpenCode, Gemini CLI, etc.) can then use Autoresearch immediately.' in text, "expected to find: " + '> Drop this file into your project root. Any AI agent (Claude Code, Codex, OpenCode, Gemini CLI, etc.) can then use Autoresearch immediately.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '7. **Git is memory** — experiments committed with `experiment:` prefix, agent reads `git log` + `git diff` before each iteration.' in text, "expected to find: " + '7. **Git is memory** — experiments committed with `experiment:` prefix, agent reads `git log` + `git diff` before each iteration.'[:80]

