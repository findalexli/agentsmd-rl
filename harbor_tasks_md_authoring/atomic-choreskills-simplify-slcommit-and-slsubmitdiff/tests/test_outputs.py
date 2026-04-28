"""Behavioral checks for atomic-choreskills-simplify-slcommit-and-slsubmitdiff (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/atomic")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sl-commit/SKILL.md')
    assert '- `sl diff` - View pending changes' in text, "expected to find: " + '- `sl diff` - View pending changes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sl-submit-diff/SKILL.md')
    assert '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode' in text, "expected to find: " + '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sl-submit-diff/SKILL.md')
    assert 'Submit commits to Phabricator for code review using `jf submit` (Meta).' in text, "expected to find: " + 'Submit commits to Phabricator for code review using `jf submit` (Meta).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sl-submit-diff/SKILL.md')
    assert '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode' in text, "expected to find: " + '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sl-commit/SKILL.md')
    assert '- `sl diff` - View pending changes' in text, "expected to find: " + '- `sl diff` - View pending changes'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sl-submit-diff/SKILL.md')
    assert '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode' in text, "expected to find: " + '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sl-submit-diff/SKILL.md')
    assert 'Submit commits to Phabricator for code review using `jf submit` (Meta).' in text, "expected to find: " + 'Submit commits to Phabricator for code review using `jf submit` (Meta).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sl-submit-diff/SKILL.md')
    assert '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode' in text, "expected to find: " + '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/sl-commit/SKILL.md')
    assert '- `sl diff` - View pending changes' in text, "expected to find: " + '- `sl diff` - View pending changes'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/sl-submit-diff/SKILL.md')
    assert '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode' in text, "expected to find: " + '2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/sl-submit-diff/SKILL.md')
    assert 'Submit commits to Phabricator for code review using `jf submit` (Meta).' in text, "expected to find: " + 'Submit commits to Phabricator for code review using `jf submit` (Meta).'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/sl-submit-diff/SKILL.md')
    assert '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode' in text, "expected to find: " + '- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode'[:80]

