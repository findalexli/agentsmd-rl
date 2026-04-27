"""Behavioral checks for ios-simulator-skill-docs-strengthen-guidance-to-use (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ios-simulator-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skill/SKILL.md')
    assert 'The 12 scripts in this skill cover all common workflows. **Only use raw tools if you need something not covered by these scripts.**' in text, "expected to find: " + 'The 12 scripts in this skill cover all common workflows. **Only use raw tools if you need something not covered by these scripts.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skill/SKILL.md')
    assert 'The 12 scripts in this skill cover all standard workflows. Raw tools should only be used for edge cases not covered:' in text, "expected to find: " + 'The 12 scripts in this skill cover all standard workflows. Raw tools should only be used for edge cases not covered:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skill/SKILL.md')
    assert '**Rule of thumb:** If one of the 12 scripts can do the job, use it. Never use raw tools for standard operations.' in text, "expected to find: " + '**Rule of thumb:** If one of the 12 scripts can do the job, use it. Never use raw tools for standard operations.'[:80]

