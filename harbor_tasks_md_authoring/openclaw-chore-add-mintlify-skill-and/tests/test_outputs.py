"""Behavioral checks for openclaw-chore-add-mintlify-skill-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mintlify/SKILL.md')
    assert 'If a user asks about migrating to Mintlify, ask if they are using ReadMe or Docusaurus. If they are, use the [@mintlify/scraping](https://www.npmjs.com/package/@mintlify/scraping) CLI to migrate conte' in text, "expected to find: " + 'If a user asks about migrating to Mintlify, ask if they are using ReadMe or Docusaurus. If they are, use the [@mintlify/scraping](https://www.npmjs.com/package/@mintlify/scraping) CLI to migrate conte'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mintlify/SKILL.md')
    assert 'When a user asks about anything related to site-wide configurations, start by understanding the [global settings](https://www.mintlify.com/docs/organize/settings). See if a setting in the `docs.json` ' in text, "expected to find: " + 'When a user asks about anything related to site-wide configurations, start by understanding the [global settings](https://www.mintlify.com/docs/organize/settings). See if a setting in the `docs.json` '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mintlify/SKILL.md')
    assert 'The [components overview](https://mintlify.com/docs/components) organizes all components by purpose: structure content, draw attention, show/hide content, document APIs, link to pages, and add visual ' in text, "expected to find: " + 'The [components overview](https://mintlify.com/docs/components) organizes all components by purpose: structure content, draw attention, show/hide content, document APIs, link to pages, and add visual '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When working with documentation, read the mintlify skill.' in text, "expected to find: " + '- When working with documentation, read the mintlify skill.'[:80]

