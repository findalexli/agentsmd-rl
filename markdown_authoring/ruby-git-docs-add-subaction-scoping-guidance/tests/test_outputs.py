"""Behavioral checks for ruby-git-docs-add-subaction-scoping-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruby-git")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert '| **Exclude (wrong sub-action)** | Option belongs to a different sub-action than the one this class implements | Omit — see [Scoping options to sub-command classes](#scoping-options-to-sub-command-cla' in text, "expected to find: " + '| **Exclude (wrong sub-action)** | Option belongs to a different sub-action than the one this class implements | Omit — see [Scoping options to sub-command classes](#scoping-options-to-sub-command-cla'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert '`Branch::List`, `Branch::Delete`), each class must include **only** the options that' in text, "expected to find: " + '`Branch::List`, `Branch::Delete`), each class must include **only** the options that'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert 'page — most git commands document options for all modes on a single page, and adding' in text, "expected to find: " + 'page — most git commands document options for all modes on a single page, and adding'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert '- [Options excluded because they belong to a different sub-action](#options-excluded-because-they-belong-to-a-different-sub-action)' in text, "expected to find: " + '- [Options excluded because they belong to a different sub-action](#options-excluded-because-they-belong-to-a-different-sub-action)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert 'This rule applies **only** to split commands. For single-class commands, include all' in text, "expected to find: " + 'This rule applies **only** to split commands. For single-class commands, include all'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert 'sub-action. Do **not** add every option from the man page — git documents all modes' in text, "expected to find: " + 'sub-action. Do **not** add every option from the man page — git documents all modes'[:80]

