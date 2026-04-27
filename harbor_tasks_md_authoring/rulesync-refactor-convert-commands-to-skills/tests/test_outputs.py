"""Behavioral checks for rulesync-refactor-convert-commands-to-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rulesync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/clean-worktrees/SKILL.md')
    assert 'name: clean-worktrees' in text, "expected to find: " + 'name: clean-worktrees'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/create-issue/SKILL.md')
    assert 'name: create-issue' in text, "expected to find: " + 'name: create-issue'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/explain-pr/SKILL.md')
    assert 'description: "Explain a PR: the background problem and the proposed solution"' in text, "expected to find: " + 'description: "Explain a PR: the background problem and the proposed solution"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/explain-pr/SKILL.md')
    assert 'name: explain-pr' in text, "expected to find: " + 'name: explain-pr'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/merge-pr/SKILL.md')
    assert 'description: Merge a pull request using gh pr merge --admin' in text, "expected to find: " + 'description: Merge a pull request using gh pr merge --admin'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/merge-pr/SKILL.md')
    assert 'name: merge-pr' in text, "expected to find: " + 'name: merge-pr'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/post-review-comment/SKILL.md')
    assert 'name: post-review-comment' in text, "expected to find: " + 'name: post-review-comment'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/release-dry-run/SKILL.md')
    assert 'name: release-dry-run' in text, "expected to find: " + 'name: release-dry-run'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/release/SKILL.md')
    assert 'name: release' in text, "expected to find: " + 'name: release'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/security-scan-diff/SKILL.md')
    assert 'name: security-scan-diff' in text, "expected to find: " + 'name: security-scan-diff'[:80]

