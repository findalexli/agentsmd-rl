"""Behavioral checks for agent-orchestrator-featskills-add-socialmediaposts-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-orchestrator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-media/SKILL.md')
    assert 'description: "Draft viral social media posts for X (Twitter) and LinkedIn. Use when asked to write, draft, create, or improve posts for X, Twitter, LinkedIn, or social media. Handles single posts, thr' in text, "expected to find: " + 'description: "Draft viral social media posts for X (Twitter) and LinkedIn. Use when asked to write, draft, create, or improve posts for X, Twitter, LinkedIn, or social media. Handles single posts, thr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-media/SKILL.md')
    assert "**Rule:** Write LinkedIn first (full story), then compress into X. Not the other way around — you can't expand a tweet into a story." in text, "expected to find: " + "**Rule:** Write LinkedIn first (full story), then compress into X. Not the other way around — you can't expand a tweet into a story."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-media/SKILL.md')
    assert '- **Blank lines matter** — double line break between paragraphs creates the visual rhythm that keeps people scrolling' in text, "expected to find: " + '- **Blank lines matter** — double line break between paragraphs creates the visual rhythm that keeps people scrolling'[:80]

