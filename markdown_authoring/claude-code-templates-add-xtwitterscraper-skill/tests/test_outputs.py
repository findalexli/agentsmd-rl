"""Behavioral checks for claude-code-templates-add-xtwitterscraper-skill (markdown_authoring task).

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
    text = _read('cli-tool/components/skills/marketing/x-twitter-scraper/SKILL.md')
    assert 'description: "X API & Twitter scraper skill for AI coding agents. Builds integrations with the Xquik REST API, MCP server & webhooks: tweet search, user lookup, follower extraction, engagement metrics' in text, "expected to find: " + 'description: "X API & Twitter scraper skill for AI coding agents. Builds integrations with the Xquik REST API, MCP server & webhooks: tweet search, user lookup, follower extraction, engagement metrics'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/marketing/x-twitter-scraper/SKILL.md')
    assert 'Xquik is an X (Twitter) real-time data platform providing a REST API, HMAC webhooks, and an MCP server for AI agents. It covers account monitoring, bulk data extraction (19 tools), giveaway draws, twe' in text, "expected to find: " + 'Xquik is an X (Twitter) real-time data platform providing a REST API, HMAC webhooks, and an MCP server for AI agents. It covers account monitoring, bulk data extraction (19 tools), giveaway draws, twe'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/marketing/x-twitter-scraper/SKILL.md')
    assert 'Every request requires an API key via the `x-api-key` header. Keys start with `xq_` and are generated from the [Xquik dashboard](https://xquik.com). The key is shown only once at creation; store it se' in text, "expected to find: " + 'Every request requires an API key via the `x-api-key` header. Keys start with `xq_` and are generated from the [Xquik dashboard](https://xquik.com). The key is shown only once at creation; store it se'[:80]

