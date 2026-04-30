"""Behavioral checks for cog-second-brain-add-scout-skill-for-urltool (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cog-second-brain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/scout/SKILL.md')
    assert 'Lightweight URL/tool triage that sits between "ignore" and `/url-dump`. Evaluates whether a URL or tool is worth saving or skipping — checking existing vault coverage, assessing relevance to the user\'' in text, "expected to find: " + 'Lightweight URL/tool triage that sits between "ignore" and `/url-dump`. Evaluates whether a URL or tool is worth saving or skipping — checking existing vault coverage, assessing relevance to the user\''[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/scout/SKILL.md')
    assert '- If `agent_mode: team` — delegate vault scanning and web fetching to parallel sub-agents (one for vault search, one for content fetch/analysis). Combine results for recommendation.' in text, "expected to find: " + '- If `agent_mode: team` — delegate vault scanning and web fetching to parallel sub-agents (one for vault search, one for content fetch/analysis). Combine results for recommendation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/scout/SKILL.md')
    assert '| web-search unavailable | For tool-name inputs (no URL), ask the user for a direct URL instead. For URL inputs, proceed normally — web-search is not needed. |' in text, "expected to find: " + '| web-search unavailable | For tool-name inputs (no URL), ask the user for a direct URL instead. For URL inputs, proceed normally — web-search is not needed. |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Purpose:** Lightweight triage that sits between "ignore" and `/url-dump`. Checks existing vault coverage, assesses relevance to your profile and interests, and recommends save or skip.' in text, "expected to find: " + '**Purpose:** Lightweight triage that sits between "ignore" and `/url-dump`. Checks existing vault coverage, assesses relevance to your profile and interests, and recommends save or skip.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Boundary with `/url-dump`:** Scout evaluates ("should I save this?"). URL-dump saves ("save this now"). If you already know you want to save, use `/url-dump` directly.' in text, "expected to find: " + '**Boundary with `/url-dump`:** Scout evaluates ("should I save this?"). URL-dump saves ("save this now"). If you already know you want to save, use `/url-dump` directly.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Description:** Evaluate URLs and tools — check vault coverage, assess relevance, recommend save or skip.' in text, "expected to find: " + '**Description:** Evaluate URLs and tools — check vault coverage, assess relevance, recommend save or skip.'[:80]

