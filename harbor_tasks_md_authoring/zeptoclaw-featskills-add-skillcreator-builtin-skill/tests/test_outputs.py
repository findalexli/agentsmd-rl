"""Behavioral checks for zeptoclaw-featskills-add-skillcreator-builtin-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zeptoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert 'Before designing anything, ask the user for 3-5 real queries or tasks the skill should handle. Collect actual example inputs and expected behaviors. Do not proceed until you have concrete use cases — ' in text, "expected to find: " + 'Before designing anything, ask the user for 3-5 real queries or tasks the skill should handle. Collect actual example inputs and expected behaviors. Do not proceed until you have concrete use cases — '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert 'For each example, ask: "What would need to be looked up, computed, or re-done each time without this skill?" The answers become the skill\'s content. Discard anything the agent already knows how to do ' in text, "expected to find: " + 'For each example, ask: "What would need to be looked up, computed, or re-done each time without this skill?" The answers become the skill\'s content. Discard anything the agent already knows how to do '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert '**Naming rules:** Lowercase letters, digits, and hyphens only. Max 64 characters. No leading, trailing, or consecutive hyphens. Prefer verb-led names: `deploy-docker`, `track-expenses`, `format-invoic' in text, "expected to find: " + '**Naming rules:** Lowercase letters, digits, and hyphens only. Max 64 characters. No leading, trailing, or consecutive hyphens. Prefer verb-led names: `deploy-docker`, `track-expenses`, `format-invoic'[:80]

