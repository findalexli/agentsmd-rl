"""Behavioral checks for everything-claude-code-featskills-add-codebaseonboarding-ski (markdown_authoring task).

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
    text = _read('skills/codebase-onboarding/SKILL.md')
    assert 'description: Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.md. Use when joining a new project or ' in text, "expected to find: " + 'description: Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.md. Use when joining a new project or '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codebase-onboarding/SKILL.md')
    assert 'Generate or update a project-specific CLAUDE.md based on detected conventions. If `CLAUDE.md` already exists, read it first and enhance it — preserve existing project-specific instructions and clearly' in text, "expected to find: " + 'Generate or update a project-specific CLAUDE.md based on detected conventions. If `CLAUDE.md` already exists, read it first and enhance it — preserve existing project-specific instructions and clearly'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codebase-onboarding/SKILL.md')
    assert 'Systematically analyze an unfamiliar codebase and produce a structured onboarding guide. Designed for developers joining a new project or setting up Claude Code in an existing repo for the first time.' in text, "expected to find: " + 'Systematically analyze an unfamiliar codebase and produce a structured onboarding guide. Designed for developers joining a new project or setting up Claude Code in an existing repo for the first time.'[:80]

