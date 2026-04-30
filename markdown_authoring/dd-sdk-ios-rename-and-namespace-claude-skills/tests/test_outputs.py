"""Behavioral checks for dd-sdk-ios-rename-and-namespace-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dd-sdk-ios")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git-branch/SKILL.md')
    assert 'name: dd-sdk-ios:git-branch' in text, "expected to find: " + 'name: dd-sdk-ios:git-branch'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git-commit/SKILL.md')
    assert 'name: dd-sdk-ios:git-commit' in text, "expected to find: " + 'name: dd-sdk-ios:git-commit'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/open-pr/SKILL.md')
    assert '**Before running the command**, show the user the proposed PR title and full body and ask for confirmation. Only run `gh pr create` after the user approves.' in text, "expected to find: " + '**Before running the command**, show the user the proposed PR title and full body and ask for confirmation. Only run `gh pr create` after the user approves.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/open-pr/SKILL.md')
    assert 'The repo has a PR template at `.github/PULL_REQUEST_TEMPLATE.md`. Read it and fill in all sections.' in text, "expected to find: " + 'The repo has a PR template at `.github/PULL_REQUEST_TEMPLATE.md`. Read it and fill in all sections.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/open-pr/SKILL.md')
    assert 'name: dd-sdk-ios:open-pr' in text, "expected to find: " + 'name: dd-sdk-ios:open-pr'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tests/SKILL.md')
    assert 'name: dd-sdk-ios:running-tests' in text, "expected to find: " + 'name: dd-sdk-ios:running-tests'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/xcode-file-management/SKILL.md')
    assert 'name: dd-sdk-ios:xcode-file-management' in text, "expected to find: " + 'name: dd-sdk-ios:xcode-file-management'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `dd-sdk-ios:xcode-file-management` | Adding, removing, moving, or renaming Swift source files |' in text, "expected to find: " + '| `dd-sdk-ios:xcode-file-management` | Adding, removing, moving, or renaming Swift source files |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `dd-sdk-ios:git-commit` | Committing changes (signed commits, message format) |' in text, "expected to find: " + '| `dd-sdk-ios:git-commit` | Committing changes (signed commits, message format) |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `dd-sdk-ios:git-branch` | Creating a new branch for a JIRA ticket or feature |' in text, "expected to find: " + '| `dd-sdk-ios:git-branch` | Creating a new branch for a JIRA ticket or feature |'[:80]

