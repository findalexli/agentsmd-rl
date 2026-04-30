"""Behavioral checks for buildwithclaude-add-xtwitterscraper-skill (markdown_authoring task).

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
    text = _read('plugins/all-skills/skills/x-twitter-scraper/SKILL.md')
    assert 'description: "X (Twitter) data extraction and monitoring via Xquik: tweet search, user lookup, follower extraction, giveaway draws, trending topics, account monitoring with webhooks, reply/retweet/quo' in text, "expected to find: " + 'description: "X (Twitter) data extraction and monitoring via Xquik: tweet search, user lookup, follower extraction, giveaway draws, trending topics, account monitoring with webhooks, reply/retweet/quo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/x-twitter-scraper/SKILL.md')
    assert 'Xquik provides a REST API, MCP server, and HMAC webhooks for X (Twitter) data. It covers tweet search, user profiles, bulk extraction (19 tools), giveaway draws, account monitoring, and trending topic' in text, "expected to find: " + 'Xquik provides a REST API, MCP server, and HMAC webhooks for X (Twitter) data. It covers tweet search, user profiles, bulk extraction (19 tools), giveaway draws, account monitoring, and trending topic'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/x-twitter-scraper/SKILL.md')
    assert 'Available filters: `mustRetweet`, `mustFollowUsername`, `filterMinFollowers`, `filterAccountAgeDays`, `filterLanguage`, `requiredKeywords`, `requiredHashtags`, `requiredMentions`, `uniqueAuthorsOnly`.' in text, "expected to find: " + 'Available filters: `mustRetweet`, `mustFollowUsername`, `filterMinFollowers`, `filterAccountAgeDays`, `filterLanguage`, `requiredKeywords`, `requiredHashtags`, `requiredMentions`, `uniqueAuthorsOnly`.'[:80]

