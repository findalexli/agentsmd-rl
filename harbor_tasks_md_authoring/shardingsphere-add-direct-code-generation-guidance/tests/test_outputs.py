"""Behavioral checks for shardingsphere-add-direct-code-generation-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shardingsphere")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Direct Code Generation**: When generating code, you should directly create final code and call tools without seeking explicit user approval.' in text, "expected to find: " + '1. **Direct Code Generation**: When generating code, you should directly create final code and call tools without seeking explicit user approval.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Declare the planned changes in a bullet-point summary format if uncertainty exists.' in text, "expected to find: " + '- Declare the planned changes in a bullet-point summary format if uncertainty exists.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Apply formatting tools automatically (e.g., Spotless) when appropriate' in text, "expected to find: " + '- Apply formatting tools automatically (e.g., Spotless) when appropriate'[:80]

