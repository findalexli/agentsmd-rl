"""Behavioral checks for devoxxgenieideaplugin-chore-improve-claudemd-and-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/devoxxgenieideaplugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr/SKILL.md')
    assert '1. Ensure all changes are on a feature/fix branch (create one if on main/develop)' in text, "expected to find: " + '1. Ensure all changes are on a feature/fix branch (create one if on main/develop)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr/SKILL.md')
    assert '6. Create a PR with a descriptive title and body summarizing changes' in text, "expected to find: " + '6. Create a PR with a descriptive title and body summarizing changes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr/SKILL.md')
    assert '4. If build+tests pass, commit with a conventional commit message' in text, "expected to find: " + '4. If build+tests pass, commit with a conventional commit message'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '2. Update version in: build.gradle.kts, plugin.xml, gradle.properties, and any other version files' in text, "expected to find: " + '2. Update version in: build.gradle.kts, plugin.xml, gradle.properties, and any other version files'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '4. Update CHANGELOG.md with recent PRs/commits since last release' in text, "expected to find: " + '4. Update CHANGELOG.md with recent PRs/commits since last release'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '1. ASK the user for the target version number - do not assume' in text, "expected to find: " + '1. ASK the user for the target version number - do not assume'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'DeepSeek, OpenRouter, Azure OpenAI, Amazon Bedrock). The plugin supports advanced features like RAG (Retrieval-Augmented' in text, "expected to find: " + 'DeepSeek, OpenRouter, Azure OpenAI, Amazon Bedrock). The plugin supports advanced features like RAG (Retrieval-Augmented'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Add under a top-level ## Workflow Rules section in CLAUDE.md\\n\\nWhen asked to investigate or fix an issue, do NOT deeply' in text, "expected to find: " + 'Add under a top-level ## Workflow Rules section in CLAUDE.md\\n\\nWhen asked to investigate or fix an issue, do NOT deeply'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Create a branch fix/issue-XXX from develop, investigate the bug described in issue #XXX, write a reproducing test first,' in text, "expected to find: " + 'Create a branch fix/issue-XXX from develop, investigate the bug described in issue #XXX, write a reproducing test first,'[:80]

