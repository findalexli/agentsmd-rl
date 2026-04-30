"""Behavioral checks for antigravity-awesome-skills-add-hierarchicalagentmemory-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hierarchical-agent-memory/SKILL.md')
    assert 'Scoped memory system that gives AI coding agents a cheat sheet for each directory instead of re-reading your entire project every prompt. Root CLAUDE.md holds global context (~200 tokens), subdirector' in text, "expected to find: " + 'Scoped memory system that gives AI coding agents a cheat sheet for each directory instead of re-reading your entire project every prompt. Root CLAUDE.md holds global context (~200 tokens), subdirector'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hierarchical-agent-memory/SKILL.md')
    assert 'description: "Scoped CLAUDE.md memory system that reduces context token spend. Creates directory-level context files, tracks savings via dashboard, and routes agents to the right sub-context."' in text, "expected to find: " + 'description: "Scoped CLAUDE.md memory system that reduces context token spend. Creates directory-level context files, tracks savings via dashboard, and routes agents to the right sub-context."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hierarchical-agent-memory/SKILL.md')
    assert '- Does not auto-update subdirectory CLAUDE.md content — you maintain those manually or via `ham audit`' in text, "expected to find: " + '- Does not auto-update subdirectory CLAUDE.md content — you maintain those manually or via `ham audit`'[:80]

