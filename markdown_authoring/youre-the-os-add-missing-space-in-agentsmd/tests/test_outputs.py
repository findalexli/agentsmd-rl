"""Behavioral checks for youre-the-os-add-missing-space-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/youre-the-os")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '* Do not make breaking changes to the [automation API](automation/api.py) unless explicitly instructed to.' in text, "expected to find: " + '* Do not make breaking changes to the [automation API](automation/api.py) unless explicitly instructed to.'[:80]

