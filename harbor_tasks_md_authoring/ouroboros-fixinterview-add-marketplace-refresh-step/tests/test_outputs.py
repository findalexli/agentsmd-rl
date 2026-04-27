"""Behavioral checks for ouroboros-fixinterview-add-marketplace-refresh-step (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '1. Run `claude plugin marketplace update ouroboros` via Bash (refresh marketplace index). If this fails, tell the user "⚠️ Marketplace refresh failed, continuing…" and proceed.' in text, "expected to find: " + '1. Run `claude plugin marketplace update ouroboros` via Bash (refresh marketplace index). If this fails, tell the user "⚠️ Marketplace refresh failed, continuing…" and proceed.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '2. Run `claude plugin update ouroboros@ouroboros` via Bash (update plugin/skills). If this fails, inform the user and stop — do NOT proceed to step 3.' in text, "expected to find: " + '2. Run `claude plugin update ouroboros@ouroboros` via Bash (update plugin/skills). If this fails, inform the user and stop — do NOT proceed to step 3.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '4. Tell the user: "Updated! Restart Claude Code to apply, then run `ooo interview` again."' in text, "expected to find: " + '4. Tell the user: "Updated! Restart Claude Code to apply, then run `ooo interview` again."'[:80]

