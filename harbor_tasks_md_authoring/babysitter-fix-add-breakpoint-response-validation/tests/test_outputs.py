"""Behavioral checks for babysitter-fix-add-breakpoint-response-validation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/babysitter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/babysitter/skills/babysit/SKILL.md')
    assert 'CRITICAL RULE: in interactive mode, NEVER auto-approve breakpoints. If AskUserQuestion returns empty, no selection, or is dismissed, treat it as NOT approved and re-ask. NEVER fabricate or synthesize ' in text, "expected to find: " + 'CRITICAL RULE: in interactive mode, NEVER auto-approve breakpoints. If AskUserQuestion returns empty, no selection, or is dismissed, treat it as NOT approved and re-ask. NEVER fabricate or synthesize '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/babysitter/skills/babysit/SKILL.md')
    assert '- If AskUserQuestion returns empty, no selection, or the user dismisses it without choosing an option: treat as **NOT approved**. Re-ask the question or keep the breakpoint in a pending/waiting state.' in text, "expected to find: " + '- If AskUserQuestion returns empty, no selection, or the user dismisses it without choosing an option: treat as **NOT approved**. Re-ask the question or keep the breakpoint in a pending/waiting state.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/babysitter/skills/babysit/SKILL.md')
    assert 'After receiving an explicit approval or rejection from the user, post the result of the breakpoint to the run by calling `task:post`.' in text, "expected to find: " + 'After receiving an explicit approval or rejection from the user, post the result of the breakpoint to the run by calling `task:post`.'[:80]

