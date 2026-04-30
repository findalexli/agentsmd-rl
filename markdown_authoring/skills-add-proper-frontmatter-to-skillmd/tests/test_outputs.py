"""Behavioral checks for skills-add-proper-frontmatter-to-skillmd (markdown_authoring task).

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
    text = _read('skills/claude-api/SKILL.md')
    assert 'description: Build, debug, and optimize Claude API / Anthropic SDK apps. Apps built with this skill should include prompt caching. TRIGGER when: code imports anthropic/@anthropic-ai/sdk; user asks to ' in text, "expected to find: " + 'description: Build, debug, and optimize Claude API / Anthropic SDK apps. Apps built with this skill should include prompt caching. TRIGGER when: code imports anthropic/@anthropic-ai/sdk; user asks to '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/SKILL.md')
    assert 'license: Complete terms in LICENSE.txt' in text, "expected to find: " + 'license: Complete terms in LICENSE.txt'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/SKILL.md')
    assert 'name: claude-api' in text, "expected to find: " + 'name: claude-api'[:80]

