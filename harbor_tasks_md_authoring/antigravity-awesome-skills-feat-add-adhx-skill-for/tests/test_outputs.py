"""Behavioral checks for antigravity-awesome-skills-feat-add-adhx-skill-for (markdown_authoring task).

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
    text = _read('skills/adhx/SKILL.md')
    assert 'ADHX provides a free API that returns clean JSON for any X post, including full long-form article content. This is far superior to scraping or browser-based approaches for LLM consumption. Works with ' in text, "expected to find: " + 'ADHX provides a free API that returns clean JSON for any X post, including full long-form article content. This is far superior to scraping or browser-based approaches for LLM consumption. Works with '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/adhx/SKILL.md')
    assert 'description: "Fetch any X/Twitter post as clean LLM-friendly JSON. Converts x.com, twitter.com, or adhx.com links into structured data with full article content, author info, and engagement metrics. N' in text, "expected to find: " + 'description: "Fetch any X/Twitter post as clean LLM-friendly JSON. Converts x.com, twitter.com, or adhx.com links into structured data with full article content, author info, and engagement metrics. N'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/adhx/SKILL.md')
    assert 'curl -sL https://raw.githubusercontent.com/itsmemeworks/adhx/main/skills/adhx/SKILL.md -o ~/.claude/skills/adhx/SKILL.md' in text, "expected to find: " + 'curl -sL https://raw.githubusercontent.com/itsmemeworks/adhx/main/skills/adhx/SKILL.md -o ~/.claude/skills/adhx/SKILL.md'[:80]

