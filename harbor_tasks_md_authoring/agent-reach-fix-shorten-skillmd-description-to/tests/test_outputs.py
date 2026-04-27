"""Behavioral checks for agent-reach-fix-shorten-skillmd-description-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-reach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Zero config for 8 channels. Use when user asks to search, read, or interact' in text, "expected to find: " + 'Zero config for 8 channels. Use when user asks to search, read, or interact'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'XiaoHongShu, Douyin, Weibo, WeChat Articles, Xiaoyuzhou Podcast, LinkedIn,' in text, "expected to find: " + 'XiaoHongShu, Douyin, Weibo, WeChat Articles, Xiaoyuzhou Podcast, LinkedIn,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert '"search twitter", "youtube transcript", "search reddit", "read this link",' in text, "expected to find: " + '"search twitter", "youtube transcript", "search reddit", "read this link",'[:80]

