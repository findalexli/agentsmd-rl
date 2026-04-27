"""Behavioral checks for buildwithclaude-add-oiloiluiuxguide-skill (markdown_authoring task).

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
    text = _read('plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md')
    assert 'description: Modern, clean UI/UX guidance + review skill. Use when you need actionable UX/UI recommendations, design principles, or a design review checklist for new features or existing systems (web/' in text, "expected to find: " + 'description: Modern, clean UI/UX guidance + review skill. Use when you need actionable UX/UI recommendations, design principles, or a design review checklist for new features or existing systems (web/'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md')
    assert 'Full skill with references available at: https://github.com/oil-oil/oiloil-ui-ux-guide' in text, "expected to find: " + 'Full skill with references available at: https://github.com/oil-oil/oiloil-ui-ux-guide'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md')
    assert '- `review`: Prioritized P0/P1/P2 fix lists with design psychology diagnosis' in text, "expected to find: " + '- `review`: Prioritized P0/P1/P2 fix lists with design psychology diagnosis'[:80]

