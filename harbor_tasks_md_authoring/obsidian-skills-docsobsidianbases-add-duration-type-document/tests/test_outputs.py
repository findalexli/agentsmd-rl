"""Behavioral checks for obsidian-skills-docsobsidianbases-add-duration-type-document (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/obsidian-bases/SKILL.md')
    assert '**IMPORTANT:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` directly. You must access a numeric field first (like `.days`), then apply number functions.' in text, "expected to find: " + '**IMPORTANT:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` directly. You must access a numeric field first (like `.days`), then apply number functions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/obsidian-bases/SKILL.md')
    assert 'When subtracting two dates, the result is a **Duration** type (not a number). Duration has its own properties and methods.' in text, "expected to find: " + 'When subtracting two dates, the result is a **Duration** type (not a number). Duration has its own properties and methods.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/obsidian-bases/SKILL.md')
    assert '# "((date(due) - today()) / 86400000).round(0)"      # Duration doesn\'t support division then round' in text, "expected to find: " + '# "((date(due) - today()) / 86400000).round(0)"      # Duration doesn\'t support division then round'[:80]

