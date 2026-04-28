"""Behavioral checks for opensre-fix-correct-misleading-filenotfounderror-message (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opensre")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert 'raise FileNotFoundError(f"input file not present: {input_path}")' in text, "expected to find: " + 'raise FileNotFoundError(f"input file not present: {input_path}")'[:80]

