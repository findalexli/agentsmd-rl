"""Behavioral checks for claude-code-templates-fix-improve-xtwitterscraper-skill-per (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/business-marketing/x-twitter-scraper/SKILL.md')
    assert 'description: "Use when the user wants to integrate with the X (Twitter) API via Xquik to search tweets, look up user profiles, extract followers, run giveaway draws, monitor accounts, or access trendi' in text, "expected to find: " + 'description: "Use when the user wants to integrate with the X (Twitter) API via Xquik to search tweets, look up user profiles, extract followers, run giveaway draws, monitor accounts, or access trendi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/business-marketing/x-twitter-scraper/SKILL.md')
    assert 'You are an expert X (Twitter) data integration specialist. You help users build applications that interact with the X platform through the Xquik API, covering tweet search, user lookups, follower extr' in text, "expected to find: " + 'You are an expert X (Twitter) data integration specialist. You help users build applications that interact with the X platform through the Xquik API, covering tweet search, user lookups, follower extr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/business-marketing/x-twitter-scraper/SKILL.md')
    assert '> **Security note:** The `${XQUIK_API_KEY}` syntax requires your MCP client to support environment variable substitution. If it does not, replace it with your actual key at runtime — but never commit ' in text, "expected to find: " + '> **Security note:** The `${XQUIK_API_KEY}` syntax requires your MCP client to support environment variable substitution. If it does not, replace it with your actual key at runtime — but never commit '[:80]

