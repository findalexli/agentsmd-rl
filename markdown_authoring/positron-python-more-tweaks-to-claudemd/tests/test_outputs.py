"""Behavioral checks for positron-python-more-tweaks-to-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/positron")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('extensions/positron-python/CLAUDE.md')
    assert '- Before running Python-related commands, if a virtual environment exists at `extensions/positron-python/.venv`, activate it' in text, "expected to find: " + '- Before running Python-related commands, if a virtual environment exists at `extensions/positron-python/.venv`, activate it'[:80]

