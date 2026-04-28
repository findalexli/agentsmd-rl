"""Behavioral checks for skymp-docs-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skymp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'If you see more than 1 unit test failed, please select one to work on and iterate with the following command.' in text, "expected to find: " + 'If you see more than 1 unit test failed, please select one to work on and iterate with the following command.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This example runs tests with only [Respawn] tag. Tags you can see in test files (.cpp).' in text, "expected to find: " + 'This example runs tests with only [Respawn] tag. Tags you can see in test files (.cpp).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All commands below must be run **inside the build directory**' in text, "expected to find: " + 'All commands below must be run **inside the build directory**'[:80]

