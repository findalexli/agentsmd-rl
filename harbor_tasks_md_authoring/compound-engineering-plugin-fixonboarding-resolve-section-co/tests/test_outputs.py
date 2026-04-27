"""Behavioral checks for compound-engineering-plugin-fixonboarding-resolve-section-co (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert 'Only read files whose content is needed to write the six sections with concrete, specific detail. The inventory already provides structure, languages, frameworks, scripts, and entry point paths -- don' in text, "expected to find: " + 'Only read files whose content is needed to write the six sections with concrete, specific detail. The inventory already provides structure, languages, frameworks, scripts, and entry point paths -- don'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert '3. **Six sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections. Section 2 may be skipped for pure infrastructur' in text, "expected to find: " + '3. **Six sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections. Section 2 may be skipped for pure infrastructur'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert 'Synthesize the inventory data and key file contents into the sections defined below. Write the file to the repo root.' in text, "expected to find: " + 'Synthesize the inventory data and key file contents into the sections defined below. Write the file to the repo root.'[:80]

