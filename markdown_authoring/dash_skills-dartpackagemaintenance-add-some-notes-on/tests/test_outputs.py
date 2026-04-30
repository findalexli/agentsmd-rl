"""Behavioral checks for dash_skills-dartpackagemaintenance-add-some-notes-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dash-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-package-maintenance/SKILL.md')
    assert '- **Do Not Amend Released Versions**: Never add new entries to a version header' in text, "expected to find: " + '- **Do Not Amend Released Versions**: Never add new entries to a version header'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-package-maintenance/SKILL.md')
    assert 'matches a released tag, increment the version (e.g., usually to `-wip`) and' in text, "expected to find: " + 'matches a released tag, increment the version (e.g., usually to `-wip`) and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-package-maintenance/SKILL.md')
    assert '- **Increment for New Changes**: If the current version in `pubspec.yaml`' in text, "expected to find: " + '- **Increment for New Changes**: If the current version in `pubspec.yaml`'[:80]

