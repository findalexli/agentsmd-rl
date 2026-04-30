"""Behavioral checks for medusa-agent-skills-fix-add-missing-name-field (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/medusa-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/medusa-dev/skills/db-generate/SKILL.md')
    assert 'name: db-generate' in text, "expected to find: " + 'name: db-generate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/medusa-dev/skills/db-migrate/SKILL.md')
    assert 'name: db-migrate' in text, "expected to find: " + 'name: db-migrate'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/medusa-dev/skills/new-user/SKILL.md')
    assert 'name: new-user' in text, "expected to find: " + 'name: new-user'[:80]

