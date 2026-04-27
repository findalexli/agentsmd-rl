"""Behavioral checks for marketingskills-fix-add-missing-sections-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert "3. What's the primary business goal? (Retention, activation, word-of-mouth, support deflection)" in text, "expected to find: " + "3. What's the primary business goal? (Retention, activation, word-of-mouth, support deflection)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert '- **churn-prevention**: For retention strategies that complement community engagement' in text, "expected to find: " + '- **churn-prevention**: For retention strategies that complement community engagement'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/community-marketing/SKILL.md')
    assert "- **customer-research**: For understanding your community members' needs and language" in text, "expected to find: " + "- **customer-research**: For understanding your community members' needs and language"[:80]

