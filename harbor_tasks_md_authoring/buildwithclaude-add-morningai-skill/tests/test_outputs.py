"""Behavioral checks for buildwithclaude-add-morningai-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/morning-ai/SKILL.md')
    assert 'description: AI news tracking skill that monitors 80+ entities across 6 free sources (Reddit, HN, GitHub, HuggingFace, arXiv, X/Twitter). Generates scored daily reports with infographics and message d' in text, "expected to find: " + 'description: AI news tracking skill that monitors 80+ entities across 6 free sources (Reddit, HN, GitHub, HuggingFace, arXiv, X/Twitter). Generates scored daily reports with infographics and message d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/morning-ai/SKILL.md')
    assert 'Daily AI news tracker that collects updates from 80+ entities across 6 sources, scores and deduplicates them, and generates a structured Markdown report.' in text, "expected to find: " + 'Daily AI news tracker that collects updates from 80+ entities across 6 sources, scores and deduplicates them, and generates a structured Markdown report.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/morning-ai/SKILL.md')
    assert '1. Collects data from 6 sources: Reddit, Hacker News, GitHub, HuggingFace, arXiv, X/Twitter' in text, "expected to find: " + '1. Collects data from 6 sources: Reddit, Hacker News, GitHub, HuggingFace, arXiv, X/Twitter'[:80]

