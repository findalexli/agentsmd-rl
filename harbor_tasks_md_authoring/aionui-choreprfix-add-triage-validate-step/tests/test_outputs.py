"""Behavioral checks for aionui-choreprfix-add-triage-validate-step (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert 'Automated workflow to resolve all issues surfaced in a pr-review report — parse summary → detect PR status → create fix branch or checkout original branch → **triage & validate** → fix by priority → q' in text, "expected to find: " + 'Automated workflow to resolve all issues surfaced in a pr-review report — parse summary → detect PR status → create fix branch or checkout original branch → **triage & validate** → fix by priority → q'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert '**Automation mode (`--automation`):** CRITICAL issues **cannot** be dismissed. If triage concludes a CRITICAL issue is a false positive, the fixer must escalate — abort the fix workflow and transfer t' in text, "expected to find: " + '**Automation mode (`--automation`):** CRITICAL issues **cannot** be dismissed. If triage concludes a CRITICAL issue is a false positive, the fixer must escalate — abort the fix workflow and transfer t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert "- The alternative's diff should not be significantly larger than the original suggestion — if it is, the change likely exceeds fix scope and should be a separate PR" in text, "expected to find: " + "- The alternative's diff should not be significantly larger than the original suggestion — if it is, the change likely exceeds fix scope and should be a separate PR"[:80]

