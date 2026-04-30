"""Behavioral checks for agent-skills-docsfrontendui-prevent-page-scroll-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-ui-engineering/SKILL.md')
    assert "if (e.key === ' ') e.preventDefault();" in text, "expected to find: " + "if (e.key === ' ') e.preventDefault();"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-ui-engineering/SKILL.md')
    assert "if (e.key === 'Enter') handleClick();" in text, "expected to find: " + "if (e.key === 'Enter') handleClick();"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-ui-engineering/SKILL.md')
    assert "if (e.key === ' ') handleClick();" in text, "expected to find: " + "if (e.key === ' ') handleClick();"[:80]

