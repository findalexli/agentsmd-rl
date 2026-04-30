"""Behavioral checks for marketingskills-docs-document-claude-code-dynamic (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'These patterns are **Claude Code only** and must not be added to `SKILL.md` files directly, as skills are designed to be cross-agent compatible (Codex, Cursor, Windsurf, etc.). Apply them locally in y' in text, "expected to find: " + 'These patterns are **Claude Code only** and must not be added to `SKILL.md` files directly, as skills are designed to be cross-agent compatible (Codex, Cursor, Windsurf, etc.). Apply them locally in y'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Why this is Claude Code-only**: Other agents that load skills will see the literal `` !`command` `` string rather than executing it, which would appear as garbled instructions. Keep cross-agent skil' in text, "expected to find: " + '**Why this is Claude Code-only**: Other agents that load skills will see the literal `` !`command` `` string rather than executing it, which would appear as garbled instructions. Keep cross-agent skil'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Claude Code supports embedding shell commands in SKILL.md using `` !`command` `` syntax. When the skill is invoked, Claude Code runs the command and injects the output inline — the model sees the resu' in text, "expected to find: " + 'Claude Code supports embedding shell commands in SKILL.md using `` !`command` `` syntax. When the skill is invoked, Claude Code runs the command and injects the output inline — the model sees the resu'[:80]

