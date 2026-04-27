"""Behavioral checks for agent-reach-docs-skillmd-metadata (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-reach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'One command install, zero config for 8 channels, agent-reach doctor for diagnostics.' in text, "expected to find: " + 'One command install, zero config for 8 channels, agent-reach doctor for diagnostics.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Search and read 14 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,' in text, "expected to find: " + 'Search and read 14 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Give your AI agent eyes to see the entire internet. 7500+ GitHub stars.' in text, "expected to find: " + 'Give your AI agent eyes to see the entire internet. 7500+ GitHub stars.'[:80]

