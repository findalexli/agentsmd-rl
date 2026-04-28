"""Behavioral checks for shopsys-add-ai-skill-for-generating (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shopsys")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert 'Until now, pages with administration domain tabs have always opened in the domain stored in the administrator session. That meant links could lead to the correct agenda, but not to the correct domain ' in text, "expected to find: " + 'Until now, pages with administration domain tabs have always opened in the domain stored in the administrator session. That meant links could lead to the correct agenda, but not to the correct domain '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert "Fill the description section with a business-value-focused explanation (1-3 paragraphs covering what changed from the user's perspective, the motivation, and the new behavior). Fill other sections as " in text, "expected to find: " + "Fill the description section with a business-value-focused explanation (1-3 paragraphs covering what changed from the user's perspective, the motivation, and the new behavior). Fill other sections as "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-description/SKILL.md')
    assert 'This change adds support for switching the selected administration domain directly from a link. As a result, links from domain-specific warnings, such as required settings notifications, can open the ' in text, "expected to find: " + 'This change adds support for switching the selected administration domain directly from a link. As a result, links from domain-specific warnings, such as required settings notifications, can open the '[:80]

