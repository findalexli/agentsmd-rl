"""Behavioral checks for ralph-fixskill-enforce-options-indentation-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ralph")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prd/SKILL.md')
    assert 'This lets users respond with "1A, 2C, 3B" for quick iteration. Remember to indent the options.' in text, "expected to find: " + 'This lets users respond with "1A, 2C, 3B" for quick iteration. Remember to indent the options.'[:80]

