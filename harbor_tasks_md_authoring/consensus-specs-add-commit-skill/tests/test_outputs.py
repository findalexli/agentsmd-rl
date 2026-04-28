"""Behavioral checks for consensus-specs-add-commit-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/consensus-specs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert 'linter makes modifications, stage these fixes. Ensure relevant tests pass if the' in text, "expected to find: " + 'linter makes modifications, stage these fixes. Ensure relevant tests pass if the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert 'The subject line (and PR title) must be written in the imperative mood. It must' in text, "expected to find: " + 'The subject line (and PR title) must be written in the imperative mood. It must'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert 'body at 72 characters. Do not use section headers. A single paragraph is ideal,' in text, "expected to find: " + 'body at 72 characters. Do not use section headers. A single paragraph is ideal,'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prepare-release/SKILL.md')
    assert 'Titles should use sentence case, not title case. Titles must be fewer than 68' in text, "expected to find: " + 'Titles should use sentence case, not title case. Titles must be fewer than 68'[:80]

