"""Behavioral checks for everything-claude-code-feat-add-clickpathaudit-skill-finds (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/click-path-audit/SKILL.md')
    assert 'description: "Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other out, produce wrong final state, or l' in text, "expected to find: " + 'description: "Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other out, produce wrong final state, or l'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/click-path-audit/SKILL.md')
    assert 'Real example: A "New Email" button called `setComposeMode(true)` then `selectThread(null)`. Both worked individually. But `selectThread` had a side effect resetting `composeMode: false`. The button di' in text, "expected to find: " + 'Real example: A "New Email" button called `setComposeMode(true)` then `selectThread(null)`. Both worked individually. But `selectThread` had a side effect resetting `composeMode: false`. The button di'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/click-path-audit/SKILL.md')
    assert 'selectThread(thread|null) → sets: {selectedThread, selectedThreadId, messages, drafts, selectedDraft, summary} RESETS: {composeMode: false, composeData: null, redraftOpen: false}' in text, "expected to find: " + 'selectThread(thread|null) → sets: {selectedThread, selectedThreadId, messages, drafts, selectedDraft, summary} RESETS: {composeMode: false, composeData: null, redraftOpen: false}'[:80]

