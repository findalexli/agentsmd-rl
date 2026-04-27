"""Behavioral checks for claude-skills-choreremembering-bump-version-to-321 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('remembering/CLAUDE.md')
    assert "**This is NON-NEGOTIABLE.** Version changes trigger releases. Committing code changes without a version bump means users won't get the update." in text, "expected to find: " + "**This is NON-NEGOTIABLE.** Version changes trigger releases. Committing code changes without a version bump means users won't get the update."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('remembering/CLAUDE.md')
    assert 'Before ANY commit to this skill, you MUST update `metadata.version` in SKILL.md frontmatter:' in text, "expected to find: " + 'Before ANY commit to this skill, you MUST update `metadata.version` in SKILL.md frontmatter:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('remembering/CLAUDE.md')
    assert '**🚨 CRITICAL: ALWAYS UPDATE SKILL VERSION WHEN MAKING CODE CHANGES 🚨**' in text, "expected to find: " + '**🚨 CRITICAL: ALWAYS UPDATE SKILL VERSION WHEN MAKING CODE CHANGES 🚨**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('remembering/SKILL.md')
    assert 'version: 3.2.1' in text, "expected to find: " + 'version: 3.2.1'[:80]

