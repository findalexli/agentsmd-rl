"""Behavioral checks for opc-skills-refactorskills-align-skillmd-frontmatter-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opc-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/banner-creator/SKILL.md')
    assert 'description: Create banners using AI image generation. Discuss format/style, generate variations, iterate with user feedback, crop to target ratio. Use when user wants to create a banner, header, hero' in text, "expected to find: " + 'description: Create banners using AI image generation. Discuss format/style, generate variations, iterate with user feedback, crop to target ratio. Use when user wants to create a banner, header, hero'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/domain-hunter/SKILL.md')
    assert 'description: Search domains, compare prices, find promo codes, get purchase recommendations. Use when user wants to buy a domain, check domain prices, find domain deals, compare registrars, or search ' in text, "expected to find: " + 'description: Search domains, compare prices, find promo codes, get purchase recommendations. Use when user wants to buy a domain, check domain prices, find domain deals, compare registrars, or search '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/logo-creator/SKILL.md')
    assert 'description: Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user feedback, crop, remove background, and export as SVG. Use when user wants to create a l' in text, "expected to find: " + 'description: Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user feedback, crop, remove background, and export as SVG. Use when user wants to create a l'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nanobanana/SKILL.md')
    assert 'description: Generate and edit images using Google Gemini 3 Pro Image (Nano Banana Pro). Supports text-to-image, image editing, various aspect ratios, and high-resolution output (2K/4K). Use when user' in text, "expected to find: " + 'description: Generate and edit images using Google Gemini 3 Pro Image (Nano Banana Pro). Supports text-to-image, image editing, various aspect ratios, and high-resolution output (2K/4K). Use when user'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/producthunt/SKILL.md')
    assert 'description: Search and retrieve content from Product Hunt. Get posts, topics, users, and collections via the GraphQL API. Use when user mentions Product Hunt, PH, or product launches.' in text, "expected to find: " + 'description: Search and retrieve content from Product Hunt. Get posts, topics, users, and collections via the GraphQL API. Use when user mentions Product Hunt, PH, or product launches.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit/SKILL.md')
    assert 'description: Search and retrieve content from Reddit. Get posts, comments, subreddit info, and user profiles via the public JSON API. Use when user mentions Reddit, a subreddit, or r/ links.' in text, "expected to find: " + 'description: Search and retrieve content from Reddit. Get posts, comments, subreddit info, and user profiles via the public JSON API. Use when user mentions Reddit, a subreddit, or r/ links.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert 'description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, and GitHub. Use when user wants to do demand ' in text, "expected to find: " + 'description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, and GitHub. Use when user wants to do demand '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-geo/SKILL.md')
    assert 'description: SEO & GEO (Generative Engine Optimization) for websites. Analyze keywords, generate schema markup, optimize for AI search engines (ChatGPT, Perplexity, Gemini, Copilot, Claude) and tradit' in text, "expected to find: " + 'description: SEO & GEO (Generative Engine Optimization) for websites. Analyze keywords, generate schema markup, optimize for AI search engines (ChatGPT, Perplexity, Gemini, Copilot, Claude) and tradit'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/twitter/SKILL.md')
    assert 'description: Search and retrieve content from Twitter/X. Get user info, tweets, replies, followers, communities, spaces, and trends via twitterapi.io. Use when user mentions Twitter, X, or tweets.' in text, "expected to find: " + 'description: Search and retrieve content from Twitter/X. Get user info, tweets, replies, followers, communities, spaces, and trends via twitterapi.io. Use when user mentions Twitter, X, or tweets.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('template/SKILL.md')
    assert 'description: Clear description of what this skill does and when to use it. Include trigger keywords and contexts inline, e.g. "Use when user wants to X, Y, or Z."' in text, "expected to find: " + 'description: Clear description of what this skill does and when to use it. Include trigger keywords and contexts inline, e.g. "Use when user wants to X, Y, or Z."'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('template/SKILL.md')
    assert '| `description` | string | ✓ | What the skill does and when to use it. Include trigger keywords and "Use when..." contexts inline. |' in text, "expected to find: " + '| `description` | string | ✓ | What the skill does and when to use it. Include trigger keywords and "Use when..." contexts inline. |'[:80]

