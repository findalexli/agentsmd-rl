"""Behavioral checks for slang-document-the-release-process-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/slang")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/slang-release-process/SKILL.md')
    assert 'description: Push a new Slang release. Triggers CI, determines the version from the sprint board, generates release notes, creates an annotated tag, and pushes it to upstream.' in text, "expected to find: " + 'description: Push a new Slang release. Triggers CI, determines the version from the sprint board, generates release notes, creates an annotated tag, and pushes it to upstream.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/slang-release-process/SKILL.md')
    assert '- **Token scopes**: The `gh` token must include `read:project` (for querying sprint info from the project board). Run `gh auth refresh --scopes read:project` to add it.' in text, "expected to find: " + '- **Token scopes**: The `gh` token must include `read:project` (for querying sprint info from the project board). Run `gh auth refresh --scopes read:project` to add it.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/slang-release-process/SKILL.md')
    assert 'Hotfix nomenclature: `vYYYY.N.H` where H increments from 1. The next sprint release note continues from the latest hotfix, not the previous sprint release.' in text, "expected to find: " + 'Hotfix nomenclature: `vYYYY.N.H` where H increments from 1. The next sprint release note continues from the latest hotfix, not the previous sprint release.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Use the `/slang-release-process` skill to push a new release. See `.claude/skills/slang-release-process/SKILL.md` for the full workflow.' in text, "expected to find: " + 'Use the `/slang-release-process` skill to push a new release. See `.claude/skills/slang-release-process/SKILL.md` for the full workflow.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '### Release Process' in text, "expected to find: " + '### Release Process'[:80]

