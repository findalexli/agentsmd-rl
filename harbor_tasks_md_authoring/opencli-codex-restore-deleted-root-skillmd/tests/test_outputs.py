"""Behavioral checks for opencli-codex-restore-deleted-root-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**When to use TS**: XHR interception (`page.installInterceptor`), infinite scrolling (`page.autoScroll`), cookie extraction, complex data transforms (like GraphQL unwrapping).' in text, "expected to find: " + '**When to use TS**: XHR interception (`page.installInterceptor`), infinite scrolling (`page.autoScroll`), cookie extraction, complex data transforms (like GraphQL unwrapping).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'tags: [cli, browser, web, chrome-extension, cdp, bilibili, zhihu, twitter, github, v2ex, hackernews, reddit, xiaohongshu, xueqiu, youtube, boss, coupang, yollomi, AI, agent]' in text, "expected to find: " + 'tags: [cli, browser, web, chrome-extension, cdp, bilibili, zhihu, twitter, github, v2ex, hackernews, reddit, xiaohongshu, xueqiu, youtube, boss, coupang, yollomi, AI, agent]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> **Note**: You must be logged into the target website in Chrome before running commands. Tabs opened during command execution are auto-closed afterwards.' in text, "expected to find: " + '> **Note**: You must be logged into the target website in Chrome before running commands. Tabs opened during command execution are auto-closed afterwards.'[:80]

