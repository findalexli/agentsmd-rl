"""Behavioral checks for skills-add-prcreate-skill-for-automated (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/pr-create/SKILL.md')
    assert 'description: Creates a pull request from current changes, monitors GitHub CI, and debugs any failures until CI passes. Use this when the user says "create pr", "make a pr", "open pull request", "submi' in text, "expected to find: " + 'description: Creates a pull request from current changes, monitors GitHub CI, and debugs any failures until CI passes. Use this when the user says "create pr", "make a pr", "open pull request", "submi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/pr-create/SKILL.md')
    assert 'Verification: include an example that demonstrates the changes in the PR as seen or used by the intended audience. For code packages, include a small, reproducible exmaple. For apps and interfaces, de' in text, "expected to find: " + 'Verification: include an example that demonstrates the changes in the PR as seen or used by the intended audience. For code packages, include a small, reproducible exmaple. For apps and interfaces, de'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/pr-create/SKILL.md')
    assert 'Summary: Give an overview of the changes in the PR. The target audience is an experienced developer who works in this code base and needs to be informed about design or architectural changes. Highligh' in text, "expected to find: " + 'Summary: Give an overview of the changes in the PR. The target audience is an experienced developer who works in this code base and needs to be informed about design or architectural changes. Highligh'[:80]

