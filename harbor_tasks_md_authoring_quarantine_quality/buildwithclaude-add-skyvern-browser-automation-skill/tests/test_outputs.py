"""Behavioral checks for buildwithclaude-add-skyvern-browser-automation-skill (markdown_authoring task).

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
    text = _read('plugins/all-skills/skills/skyvern/SKILL.md')
    assert 'description: "AI-powered browser automation — navigate sites, fill forms, extract structured data, log in with stored credentials, and build reusable multi-step workflows using natural language. Insta' in text, "expected to find: " + 'description: "AI-powered browser automation — navigate sites, fill forms, extract structured data, log in with stored credentials, and build reusable multi-step workflows using natural language. Insta'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/skyvern/SKILL.md')
    assert 'Control a real browser with natural language. Skyvern uses Vision LLMs and computer vision instead of brittle XPath/DOM selectors, so automations survive UI changes.' in text, "expected to find: " + 'Control a real browser with natural language. Skyvern uses Vision LLMs and computer vision instead of brittle XPath/DOM selectors, so automations survive UI changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/skyvern/SKILL.md')
    assert '- **Reusable workflows** — 23 block types, parameterized runs, cached scripts (10-100x faster on repeat)' in text, "expected to find: " + '- **Reusable workflows** — 23 block types, parameterized runs, cached scripts (10-100x faster on repeat)'[:80]

