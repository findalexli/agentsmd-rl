"""Behavioral checks for antigravity-awesome-skills-feat-add-wordpresscentrichighseoo (markdown_authoring task).

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
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert 'description: "Use this skill when the user asks to write a blog post, article, or SEO content. This applies a professional structure, truth boxes, click-bait-free accurate information, and outputs dir' in text, "expected to find: " + 'description: "Use this skill when the user asks to write a blog post, article, or SEO content. This applies a professional structure, truth boxes, click-bait-free accurate information, and outputs dir'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert 'Your task is to create a long-form, high-quality, SEO-optimized blog post that is clear, engaging, and ready to publish directly in WordPress.' in text, "expected to find: " + 'Your task is to create a long-form, high-quality, SEO-optimized blog post that is clear, engaging, and ready to publish directly in WordPress.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md')
    assert '- Requirement: Provide citation-backed estimates with a verifiable source or an explicit "no reliable estimate available" response.' in text, "expected to find: " + '- Requirement: Provide citation-backed estimates with a verifiable source or an explicit "no reliable estimate available" response.'[:80]

