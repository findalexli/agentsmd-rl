"""Behavioral checks for hypershift-nojira-docsai-add-reference-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hypershift")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The Effective Go skill is automatically enabled for all Go development. Just ask Claude to write or review Go code, and best practices will be automatically applied.' in text, "expected to find: " + 'The Effective Go skill is automatically enabled for all Go development. Just ask Claude to write or review Go code, and best practices will be automatically applied.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Please also refer to @AGENTS.md for guidance to all AI agents when working with code in this repository.' in text, "expected to find: " + 'Please also refer to @AGENTS.md for guidance to all AI agents when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository includes Claude Code specific configuration for enhanced development assistance.' in text, "expected to find: " + 'This repository includes Claude Code specific configuration for enhanced development assistance.'[:80]

