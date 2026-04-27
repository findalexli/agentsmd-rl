"""Behavioral checks for posthog-chorellma-teach-skillsstore-skill-the (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('products/llm_analytics/skills/skills-store/SKILL.md')
    assert 'allowed-tools: mcp__posthog__skill-list, mcp__posthog__skill-get, mcp__posthog__skill-create, mcp__posthog__skill-update, mcp__posthog__skill-file-get, mcp__posthog__skill-file-create, mcp__posthog__s' in text, "expected to find: " + 'allowed-tools: mcp__posthog__skill-list, mcp__posthog__skill-get, mcp__posthog__skill-create, mcp__posthog__skill-update, mcp__posthog__skill-file-get, mcp__posthog__skill-file-create, mcp__posthog__s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('products/llm_analytics/skills/skills-store/SKILL.md')
    assert 'Passing `files` to `skill-update` replaces ALL bundled files — anything not in the array is dropped. Only use this when you intentionally want to wipe and reseed the bundle. For everything else, prefe' in text, "expected to find: " + 'Passing `files` to `skill-update` replaces ALL bundled files — anything not in the array is dropped. Only use this when you intentionally want to wipe and reseed the bundle. For everything else, prefe'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('products/llm_analytics/skills/skills-store/SKILL.md')
    assert "Pick the most surgical primitive for what you're changing — the API offers several so you don't have to round-trip the whole skill to tweak one part. Anything you don't touch is carried forward from t" in text, "expected to find: " + "Pick the most surgical primitive for what you're changing — the API offers several so you don't have to round-trip the whole skill to tweak one part. Anything you don't touch is carried forward from t"[:80]

