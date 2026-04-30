"""Behavioral checks for clusterfuzz-update-agentsmd-with-linting-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/clusterfuzz")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "It's possible to get into a state where linting and formatting contradict each other. In this case, STOP, the human will fix it." in text, "expected to find: " + "It's possible to get into a state where linting and formatting contradict each other. In this case, STOP, the human will fix it."[:80]

