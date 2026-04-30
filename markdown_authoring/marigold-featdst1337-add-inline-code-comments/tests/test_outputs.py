"""Behavioral checks for marigold-featdst1337-add-inline-code-comments (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marigold")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'If step 5 recorded a visual regression issue (status is "not started", "stale", or "failed"), include it as an additional inline comment targeting the first UI-affecting file in the diff. This is a **' in text, "expected to find: " + 'If step 5 recorded a visual regression issue (status is "not started", "stale", or "failed"), include it as an additional inline comment targeting the first UI-affecting file in the diff. This is a **'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'This step ensures the user sees the exact content before it goes to GitHub and has a final say on the review event type. Use the selected event (`REQUEST_CHANGES` or `COMMENT`) as the `event` field in' in text, "expected to find: " + 'This step ensures the user sees the exact content before it goes to GitHub and has a final say on the review event type. Use the selected event (`REQUEST_CHANGES` or `COMMENT`) as the `event` field in'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'If the workflow is **running** or **passed (up to date)**, no inline comment is needed — just report the status in the review report\'s overview table (e.g., "Visual Regression | Passed" or "Visual Reg' in text, "expected to find: " + 'If the workflow is **running** or **passed (up to date)**, no inline comment is needed — just report the status in the review report\'s overview table (e.g., "Visual Regression | Passed" or "Visual Reg'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/references/review-checklist.md')
    assert '- Missing, stale, or failed visual regression tests when UI-affecting files are changed' in text, "expected to find: " + '- Missing, stale, or failed visual regression tests when UI-affecting files are changed'[:80]

