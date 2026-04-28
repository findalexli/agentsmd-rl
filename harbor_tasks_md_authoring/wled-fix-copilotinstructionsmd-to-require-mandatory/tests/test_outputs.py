"""Behavioral checks for wled-fix-copilotinstructionsmd-to-require-mandatory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wled")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**When validating your changes before finishing, you MUST wait for the hardware build to complete successfully. Set the timeout appropriately and be patient.**' in text, "expected to find: " + '**When validating your changes before finishing, you MUST wait for the hardware build to complete successfully. Set the timeout appropriately and be patient.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**If any of these validation steps fail, you MUST fix the issues before finishing. Do NOT mark work as complete with failing builds or tests.**' in text, "expected to find: " + '**If any of these validation steps fail, you MUST fix the issues before finishing. Do NOT mark work as complete with failing builds or tests.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Match this workflow in your local development to ensure CI success. Do not mark work complete until you have validated builds locally.**' in text, "expected to find: " + '**Match this workflow in your local development to ensure CI success. Do not mark work complete until you have validated builds locally.**'[:80]

