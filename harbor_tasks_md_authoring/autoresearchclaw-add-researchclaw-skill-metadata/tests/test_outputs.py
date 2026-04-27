"""Behavioral checks for autoresearchclaw-add-researchclaw-skill-metadata (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autoresearchclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/researchclaw/SKILL.md')
    assert 'description: Run the ResearchClaw autonomous research pipeline from a topic, config, and output directory.' in text, "expected to find: " + 'description: Run the ResearchClaw autonomous research pipeline from a topic, config, and output directory.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/researchclaw/SKILL.md')
    assert 'name: researchclaw' in text, "expected to find: " + 'name: researchclaw'[:80]

