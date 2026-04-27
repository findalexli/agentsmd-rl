"""Behavioral checks for workerd-refine-the-opencode-v8-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workerd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/update-v8/SKILL.md')
    assert '**Never** take irreversible actions (like dropping patches or updating hashes) without explicit confirmation.' in text, "expected to find: " + '**Never** take irreversible actions (like dropping patches or updating hashes) without explicit confirmation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/update-v8/SKILL.md')
    assert '**Always** confirm with the human before replacing patches. If any patches were dropped or added,' in text, "expected to find: " + '**Always** confirm with the human before replacing patches. If any patches were dropped or added,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/update-v8/SKILL.md')
    assert '**Never** push the branch for review without a human review of the patch changes.' in text, "expected to find: " + '**Never** push the branch for review without a human review of the patch changes.'[:80]

