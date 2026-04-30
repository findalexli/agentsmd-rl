"""Behavioral checks for surrealdb-add-cursor-rule-for-pull (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/surrealdb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert 'Briefly assess security implications. If there are none, state why (e.g. "documentation-only change", "build profile change only"). If there are security implications, assign the `security-review` lab' in text, "expected to find: " + 'Briefly assess security implications. If there are none, state why (e.g. "documentation-only change", "build profile change only"). If there are security implications, assign the `security-review` lab'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert "If there is a specific testing strategy, and new tests are added, describe the changes. Otherwise insert 'GitHub Actions testing'." in text, "expected to find: " + "If there is a specific testing strategy, and new tests are added, describe the changes. Otherwise insert 'GitHub Actions testing'."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert 'Link related issues using `Closes #123` or `Fixes #123` to auto-close them. If none, check "No related issues".' in text, "expected to find: " + 'Link related issues using `Closes #123` or `Fixes #123` to auto-close them. If none, check "No related issues".'[:80]

