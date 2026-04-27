"""Behavioral checks for claude-code-plugins-plus-skills-featnotionpack-build-skill-8 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-debug-bundle/SKILL.md')
    assert 'Collect diagnostic information for Notion API issues: SDK version, token validity, database access, page sharing status, rate limits, and platform health. The Notion API requires integrations to be ex' in text, "expected to find: " + 'Collect diagnostic information for Notion API issues: SDK version, token validity, database access, page sharing status, rate limits, and platform health. The Notion API requires integrations to be ex'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-debug-bundle/SKILL.md')
    assert '**SAFE TO INCLUDE:** Error codes/messages, HTTP status codes, latencies, SDK versions, platform status, page/database IDs (non-sensitive metadata)' in text, "expected to find: " + '**SAFE TO INCLUDE:** Error codes/messages, HTTP status codes, latencies, SDK versions, platform status, page/database IDs (non-sensitive metadata)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-debug-bundle/SKILL.md')
    assert '- [Integration Setup Guide](https://developers.notion.com/docs/create-a-notion-integration) — creating and configuring integrations' in text, "expected to find: " + '- [Integration Setup Guide](https://developers.notion.com/docs/create-a-notion-integration) — creating and configuring integrations'[:80]

