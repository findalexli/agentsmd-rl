"""Behavioral checks for fundamental-ngx-chore-add-claudemd-cursorrules-windsurfrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fundamental-ngx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'Read and follow AGENTS.md for all development conventions.' in text, "expected to find: " + 'Read and follow AGENTS.md for all development conventions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.windsurfrules')
    assert 'Read and follow AGENTS.md for all development conventions.' in text, "expected to find: " + 'Read and follow AGENTS.md for all development conventions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read and follow AGENTS.md for all development conventions.' in text, "expected to find: " + 'Read and follow AGENTS.md for all development conventions.'[:80]

