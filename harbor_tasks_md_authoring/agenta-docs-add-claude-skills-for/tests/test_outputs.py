"""Behavioral checks for agenta-docs-add-claude-skills-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agenta")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-announcement/SKILL.md')
    assert 'description: Helps add announcement cards to the sidebar banner system. Use when adding changelog entries, feature announcements, updates, or promotional banners to the Agenta sidebar. Handles both si' in text, "expected to find: " + 'description: Helps add announcement cards to the sidebar banner system. Use when adding changelog entries, feature announcements, updates, or promotional banners to the Agenta sidebar. Handles both si'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-announcement/SKILL.md')
    assert '**Note**: This skill focuses on simple changelog announcements. For custom banners with complex logic, consult the SidebarBanners README or ask for guidance on creating custom banner components.' in text, "expected to find: " + '**Note**: This skill focuses on simple changelog announcements. For custom banners with complex logic, consult the SidebarBanners README or ask for guidance on creating custom banner components.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-announcement/SKILL.md')
    assert 'This skill helps you add announcement cards to the Agenta sidebar banner system. Announcement cards appear at the bottom of the sidebar and can be dismissed by users.' in text, "expected to find: " + 'This skill helps you add announcement cards to the Agenta sidebar banner system. Announcement cards appear at the bottom of the sidebar and can be dismissed by users.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-changelog-announcement/SKILL.md')
    assert 'description: Use this skill to create and publish changelog announcements for new features, improvements, or bug fixes. This skill handles the complete workflow - creating detailed changelog documenta' in text, "expected to find: " + 'description: Use this skill to create and publish changelog announcements for new features, improvements, or bug fixes. This skill handles the complete workflow - creating detailed changelog documenta'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-changelog-announcement/SKILL.md')
    assert 'The new session browser shows key metrics like total cost, latency, and token usage per conversation. Open any session to see all traces with their parent-child relationships. This makes debugging cha' in text, "expected to find: " + 'The new session browser shows key metrics like total cost, latency, and token usage per conversation. Open any session to see all traces with their parent-child relationships. This makes debugging cha'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-changelog-announcement/SKILL.md')
    assert 'Chat sessions bring conversation-level observability to Agenta. You can now group related traces from multi-turn conversations together, making it easy to analyze complete user interactions rather tha' in text, "expected to find: " + 'Chat sessions bring conversation-level observability to Agenta. You can now group related traces from multi-turn conversations together, making it easy to analyze complete user interactions rather tha'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-social-announcement/SKILL.md')
    assert '**Provider costs upfront.** You can now see the cost per million tokens directly in the model selection dropdown — helping you make informed decisions about which model to use.' in text, "expected to find: " + '**Provider costs upfront.** You can now see the cost per million tokens directly in the model selection dropdown — helping you make informed decisions about which model to use.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-social-announcement/SKILL.md')
    assert '**Evaluations from the Playground.** Start an evaluation run without leaving the Playground, keeping you in flow when iterating on prompts.' in text, "expected to find: " + '**Evaluations from the Playground.** Start an evaluation run without leaving the Playground, keeping you in flow when iterating on prompts.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-social-announcement/SKILL.md')
    assert 'This skill creates authentic social media announcements for LinkedIn, Twitter/X, and Slack that avoid common AI writing patterns.' in text, "expected to find: " + 'This skill creates authentic social media announcements for LinkedIn, Twitter/X, and Slack that avoid common AI writing patterns.'[:80]

