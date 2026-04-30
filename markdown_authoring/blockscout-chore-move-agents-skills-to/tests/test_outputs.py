"""Behavioral checks for blockscout-chore-move-agents-skills-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/blockscout")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/alias-nested-modules/SKILL.md')
    assert '.agents/skills/alias-nested-modules/SKILL.md' in text, "expected to find: " + '.agents/skills/alias-nested-modules/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/alphabetically-ordered-aliases/SKILL.md')
    assert '.agents/skills/alphabetically-ordered-aliases/SKILL.md' in text, "expected to find: " + '.agents/skills/alphabetically-ordered-aliases/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code-formatting/SKILL.md')
    assert '.agents/skills/code-formatting/SKILL.md' in text, "expected to find: " + '.agents/skills/code-formatting/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/compare-against-empty-list/SKILL.md')
    assert '.agents/skills/compare-against-empty-list/SKILL.md' in text, "expected to find: " + '.agents/skills/compare-against-empty-list/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/compile-project/SKILL.md')
    assert '.agents/skills/compile-project/SKILL.md' in text, "expected to find: " + '.agents/skills/compile-project/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ecto-migration/SKILL.md')
    assert '.agents/skills/ecto-migration/SKILL.md' in text, "expected to find: " + '.agents/skills/ecto-migration/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/efficient-list-building/SKILL.md')
    assert '.agents/skills/efficient-list-building/SKILL.md' in text, "expected to find: " + '.agents/skills/efficient-list-building/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/heavy-db-index-operation/SKILL.md')
    assert '.agents/skills/heavy-db-index-operation/SKILL.md' in text, "expected to find: " + '.agents/skills/heavy-db-index-operation/SKILL.md'[:80]

