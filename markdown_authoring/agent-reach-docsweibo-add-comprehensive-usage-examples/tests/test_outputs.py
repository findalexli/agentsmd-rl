"""Behavioral checks for agent-reach-docsweibo-add-comprehensive-usage-examples (markdown_authoring task).

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
    assert '> Zero config. No login needed. Uses mobile API with auto visitor cookies.' in text, "expected to find: " + '> Zero config. No login needed. Uses mobile API with auto visitor cookies.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'mcporter call \'weibo.get_comments(mid: "5099916367123456", limit: 50)\'' in text, "expected to find: " + 'mcporter call \'weibo.get_comments(mid: "5099916367123456", limit: 50)\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'mcporter call \'weibo.get_hot_feeds(uid: "1195230310", limit: 10)\'' in text, "expected to find: " + 'mcporter call \'weibo.get_hot_feeds(uid: "1195230310", limit: 10)\''[:80]

