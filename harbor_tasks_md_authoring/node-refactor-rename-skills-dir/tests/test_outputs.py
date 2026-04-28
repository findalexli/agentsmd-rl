"""Behavioral checks for node-refactor-rename-skills-dir (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/node")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-env/SKILL.md')
    assert '.agents/skills/setup-env/SKILL.md' in text, "expected to find: " + '.agents/skills/setup-env/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/smartcontracts/SKILL.md')
    assert '.agents/skills/smartcontracts/SKILL.md' in text, "expected to find: " + '.agents/skills/smartcontracts/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vanity/SKILL.md')
    assert '.agents/skills/vanity/SKILL.md' in text, "expected to find: " + '.agents/skills/vanity/SKILL.md'[:80]

