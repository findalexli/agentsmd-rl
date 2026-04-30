"""Behavioral checks for planner-chore-replace-claudemd-with-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/planner")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Docker setup exists in this repository (`bin/d*` commands) but is **not used** for development work with Claude Code, OpenCode, etc.' in text, "expected to find: " + 'Docker setup exists in this repository (`bin/d*` commands) but is **not used** for development work with Claude Code, OpenCode, etc.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides guidance to AI agents when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to AI agents when working with code in this repository.'[:80]

