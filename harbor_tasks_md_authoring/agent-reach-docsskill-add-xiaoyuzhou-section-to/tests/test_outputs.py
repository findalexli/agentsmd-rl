"""Behavioral checks for agent-reach-docsskill-add-xiaoyuzhou-section-to (markdown_authoring task).

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
    assert '~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"' in text, "expected to find: " + '~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Xiaoyuzhou Podcast (小宇宙播客), LinkedIn, Instagram, V2EX, RSS, Exa web search, and any web page.' in text, "expected to find: " + 'Xiaoyuzhou Podcast (小宇宙播客), LinkedIn, Instagram, V2EX, RSS, Exa web search, and any web page.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Search and read 16 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,' in text, "expected to find: " + 'Search and read 16 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,'[:80]

