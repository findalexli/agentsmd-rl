"""Behavioral checks for buildwithclaude-add-agentanalytics-skill (markdown_authoring task).

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
    text = _read('plugins/all-skills/skills/agent-analytics/SKILL.md')
    assert 'The `create` command returns a tracking snippet with your project token — add it before `</body>`. It auto-tracks `page_view` events with path, referrer, browser, OS, device, screen size, and UTM para' in text, "expected to find: " + 'The `create` command returns a tracking snippet with your project token — add it before `</body>`. It auto-tracks `page_view` events with path, referrer, browser, OS, device, screen size, and UTM para'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/agent-analytics/SKILL.md')
    assert 'You are adding analytics tracking using Agent Analytics — the analytics platform your AI agent can actually use. Built for developers who ship lots of projects and want their AI agent to track, analyz' in text, "expected to find: " + 'You are adding analytics tracking using Agent Analytics — the analytics platform your AI agent can actually use. Built for developers who ship lots of projects and want their AI agent to track, analyz'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/agent-analytics/SKILL.md')
    assert '**Get an API key:** Sign up at [agentanalytics.sh](https://agentanalytics.sh) and generate a key from the dashboard. Alternatively, self-host the open-source version from [GitHub](https://github.com/A' in text, "expected to find: " + '**Get an API key:** Sign up at [agentanalytics.sh](https://agentanalytics.sh) and generate a key from the dashboard. Alternatively, self-host the open-source version from [GitHub](https://github.com/A'[:80]

