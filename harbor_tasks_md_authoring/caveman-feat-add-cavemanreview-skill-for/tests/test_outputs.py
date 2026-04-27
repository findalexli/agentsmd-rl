"""Behavioral checks for caveman-feat-add-cavemanreview-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caveman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-review/SKILL.md')
    assert 'Drop terse mode for: security findings (CVE-class bugs need full explanation + reference), architectural disagreements (need rationale, not just a one-liner), and onboarding contexts where the author ' in text, "expected to find: " + 'Drop terse mode for: security findings (CVE-class bugs need full explanation + reference), architectural disagreements (need rationale, not just a one-liner), and onboarding contexts where the author '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-review/SKILL.md')
    assert '❌ "I noticed that on line 42 you\'re not checking if the user object is null before accessing the email property. This could potentially cause a crash if the user is not found in the database. You migh' in text, "expected to find: " + '❌ "I noticed that on line 42 you\'re not checking if the user object is null before accessing the email property. This could potentially cause a crash if the user is not found in the database. You migh'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-review/SKILL.md')
    assert 'Reviews only — does not write the code fix, does not approve/request-changes, does not run linters. Output the comment(s) ready to paste into the PR. "stop caveman-review" or "normal mode": revert to ' in text, "expected to find: " + 'Reviews only — does not write the code fix, does not approve/request-changes, does not run linters. Output the comment(s) ready to paste into the PR. "stop caveman-review" or "normal mode": revert to '[:80]

