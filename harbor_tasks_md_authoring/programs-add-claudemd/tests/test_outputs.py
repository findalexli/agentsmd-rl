"""Behavioral checks for programs-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/programs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Getting unique transaction signatures:** When testing error cases that call the same instruction multiple times (e.g., verifying an action fails after state changes), add a `ComputeBudgetProgram.set' in text, "expected to find: " + '**Getting unique transaction signatures:** When testing error cases that call the same instruction multiple times (e.g., verifying an action fails after state changes), add a `ComputeBudgetProgram.set'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `token::mint` / `token::authority` - allows any token account with matching mint/authority (use only when flexibility is intentionally needed, e.g., source accounts where user may fund from non-ATA)' in text, "expected to find: " + '- `token::mint` / `token::authority` - allows any token account with matching mint/authority (use only when flexibility is intentionally needed, e.g., source accounts where user may fund from non-ATA)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Exceptions: Keep messages in `expectError()` calls and `assert.fail()` within try-catch blocks, since those are part of error handling patterns and help identify which check failed.' in text, "expected to find: " + 'Exceptions: Keep messages in `expectError()` calls and `assert.fail()` within try-catch blocks, since those are part of error handling patterns and help identify which check failed.'[:80]

