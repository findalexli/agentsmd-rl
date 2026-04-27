"""Behavioral checks for antigravity-awesome-skills-feat-add-socialpostwriterseo-skil (markdown_authoring task).

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
    text = _read('skills/social-post-writer-seo/SKILL.md')
    assert 'Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.' in text, "expected to find: " + 'Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-post-writer-seo/SKILL.md')
    assert 'description: "Social Media Strategist and Content Writer. Creates clear, engaging social media posts for Instagram, LinkedIn, and Facebook."' in text, "expected to find: " + 'description: "Social Media Strategist and Content Writer. Creates clear, engaging social media posts for Instagram, LinkedIn, and Facebook."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-post-writer-seo/SKILL.md')
    assert '- Use this skill when you need a clear, engaging, and accurate social media post for Instagram, LinkedIn, or Facebook.' in text, "expected to find: " + '- Use this skill when you need a clear, engaging, and accurate social media post for Instagram, LinkedIn, or Facebook.'[:80]

