"""Behavioral checks for marketingskills-feat-add-communitymarketing-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert 'description: Build and leverage online communities to drive product growth and brand loyalty. Use when the user wants to create a community strategy, grow a Discord or Slack community, manage a forum ' in text, "expected to find: " + 'description: Build and leverage online communities to drive product growth and brand loyalty. Use when the user wants to create a community strategy, grow a Discord or Slack community, manage a forum '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert 'You are an expert community builder and community-led growth strategist. Your goal is to help the user design, launch, and grow a community that creates genuine value for members while driving measura' in text, "expected to find: " + 'You are an expert community builder and community-led growth strategist. Your goal is to help the user design, launch, and grow a community that creates genuine value for members while driving measura'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert 'If `.agents/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Use that context and only ask for information not already' in text, "expected to find: " + 'If `.agents/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Use that context and only ask for information not already'[:80]

