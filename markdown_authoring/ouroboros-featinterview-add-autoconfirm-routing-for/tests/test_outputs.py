"""Behavioral checks for ouroboros-featinterview-add-autoconfirm-routing-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '- The user can correct at any time by saying "that\'s wrong" — re-send correction to MCP' in text, "expected to find: " + '- The user can correct at any time by saying "that\'s wrong" — re-send correction to MCP'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert 'for auto-confirm (inferred from patterns, multiple candidates, or no manifest match):' in text, "expected to find: " + 'for auto-confirm (inferred from patterns, multiple candidates, or no manifest match):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '- For high-confidence factual questions (PATH 1a), auto-confirm and notify the user' in text, "expected to find: " + '- For high-confidence factual questions (PATH 1a), auto-confirm and notify the user'[:80]

