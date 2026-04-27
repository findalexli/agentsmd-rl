"""Behavioral checks for skills-add-prompt-to-evaluate-skills (markdown_authoring task).

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
    text = _read('.github/prompts/evaluate-skill-descriptions.prompt.md')
    assert "The `description` field in each skill's frontmatter is the **only** information a coding agent sees (alongside the skill name) when deciding whether to load the skill. Agents use progressive loading —" in text, "expected to find: " + "The `description` field in each skill's frontmatter is the **only** information a coding agent sees (alongside the skill name) when deciding whether to load the skill. Agents use progressive loading —"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/evaluate-skill-descriptions.prompt.md')
    assert 'This repo contains several skills for helping AI coding agents like GitHub Copilot and Claude Code with .NET-related coding tasks. Evaluate how good the description is in the YAML front matter for eac' in text, "expected to find: " + 'This repo contains several skills for helping AI coding agents like GitHub Copilot and Claude Code with .NET-related coding tasks. Evaluate how good the description is in the YAML front matter for eac'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/evaluate-skill-descriptions.prompt.md')
    assert '| **5** | Excellent — clearly states what, when to use, when NOT to use, and key capabilities; includes concrete trigger phrases, user-intent signals, and clear non-goals/boundaries |' in text, "expected to find: " + '| **5** | Excellent — clearly states what, when to use, when NOT to use, and key capabilities; includes concrete trigger phrases, user-intent signals, and clear non-goals/boundaries |'[:80]

