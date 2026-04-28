"""Behavioral checks for antigravity-awesome-skills-fixsecurityengineer-correct-risk- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ethical-hacking-methodology/SKILL.md')
    assert '> AUTHORIZED USE ONLY: Use this skill only for authorized penetration testing engagements, defensive validation, or controlled educational environments.' in text, "expected to find: " + '> AUTHORIZED USE ONLY: Use this skill only for authorized penetration testing engagements, defensive validation, or controlled educational environments.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ethical-hacking-methodology/SKILL.md')
    assert 'risk: offensive' in text, "expected to find: " + 'risk: offensive'[:80]

