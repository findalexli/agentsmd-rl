"""Behavioral checks for antigravity-awesome-skills-docswordpressseoskill-update-skil (markdown_authoring task).

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
    assert 'This skill is designed to help users create high-quality, engaging, and platform-optimized social media content. It focuses on clarity, readability, and platform-specific nuances for Instagram, Linked' in text, "expected to find: " + 'This skill is designed to help users create high-quality, engaging, and platform-optimized social media content. It focuses on clarity, readability, and platform-specific nuances for Instagram, Linked'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-post-writer-seo/SKILL.md')
    assert 'Based on the inputs, it follows strict writing rules to ensure simplicity, factual accuracy, and engagement. It structures the post with a hook, context, value, and a call to action.' in text, "expected to find: " + 'Based on the inputs, it follows strict writing rules to ensure simplicity, factual accuracy, and engagement. It structures the post with a hook, context, value, and a call to action.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/social-post-writer-seo/SKILL.md')
    assert 'Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.' in text, "expected to find: " + 'Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert 'This skill is designed for Senior Content Strategists and Expert Copywriters to create high-quality, long-form blog posts that are ready for direct publication in WordPress. It emphasizes professional' in text, "expected to find: " + 'This skill is designed for Senior Content Strategists and Expert Copywriters to create high-quality, long-form blog posts that are ready for direct publication in WordPress. It emphasizes professional'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert 'The agent follows a structured prompt to generate a clickable contents section, a truth box, well-structured sections with tables, common misconceptions, and a short FAQ.' in text, "expected to find: " + 'The agent follows a structured prompt to generate a clickable contents section, a truth box, well-structured sections with tables, common misconceptions, and a short FAQ.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert 'The skill requires a Title, Primary Keyword, Intent, and Niche/Industry. It also prompts for Yoast SEO preference and image count if not provided.' in text, "expected to find: " + 'The skill requires a Title, Primary Keyword, Intent, and Niche/Industry. It also prompts for Yoast SEO preference and image count if not provided.'[:80]

