"""Behavioral checks for autoskill-improve-changeloggenerator-skill-structure-eval (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autoskill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md')
    assert 'Omit any empty section. Order: breaking changes, features, improvements, fixes, security. If the repo already has a `CHANGELOG.md` or `CHANGELOG_STYLE.md`, match its existing conventions instead.' in text, "expected to find: " + 'Omit any empty section. Order: breaking changes, features, improvements, fixes, security. If the repo already has a `CHANGELOG.md` or `CHANGELOG_STYLE.md`, match its existing conventions instead.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md')
    assert 'For non-conventional messages, infer category from content. Exclude purely internal commits (test infra, CI config, linting, dependency bumps with no user impact).' in text, "expected to find: " + 'For non-conventional messages, infer category from content. Exclude purely internal commits (test infra, CI config, linting, dependency bumps with no user impact).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md')
    assert "4. Write to `CHANGELOG.md` (prepend above existing content) or print inline, based on the user's request" in text, "expected to find: " + "4. Write to `CHANGELOG.md` (prepend above existing content) or print inline, based on the user's request"[:80]

