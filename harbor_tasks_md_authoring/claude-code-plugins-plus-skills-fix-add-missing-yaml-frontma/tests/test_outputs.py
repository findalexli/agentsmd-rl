"""Behavioral checks for claude-code-plugins-plus-skills-fix-add-missing-yaml-frontma (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/skill-auditor.md')
    assert 'description: Audit and fix Claude Code SKILL.md files to meet enterprise compliance standards. Analyzes frontmatter, required sections, and style. Use when you need to validate or repair skills in a p' in text, "expected to find: " + 'description: Audit and fix Claude Code SKILL.md files to meet enterprise compliance standards. Analyzes frontmatter, required sections, and style. Use when you need to validate or repair skills in a p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/skill-auditor.md')
    assert 'name: skill-auditor' in text, "expected to find: " + 'name: skill-auditor'[:80]

