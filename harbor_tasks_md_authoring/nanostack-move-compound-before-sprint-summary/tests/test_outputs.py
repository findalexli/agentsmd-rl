"""Behavioral checks for nanostack-move-compound-before-sprint-summary (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**3. What could come next.** Suggest 2-3 concrete extensions as `/feature` commands the user can run immediately.' in text, "expected to find: " + '**3. What could come next.** Suggest 2-3 concrete extensions as `/feature` commands the user can run immediately.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert 'Do not ask. Do not skip. Compound reads the sprint artifacts and saves solutions for future sprints.' in text, "expected to find: " + 'Do not ask. Do not skip. Compound reads the sprint artifacts and saves solutions for future sprints.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**Then: close the sprint.** This is the last thing the user sees. Make it count.' in text, "expected to find: " + '**Then: close the sprint.** This is the last thing the user sees. Make it count.'[:80]

