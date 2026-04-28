"""Behavioral checks for mcbopomofo-adjusts-copilot-code-review-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcbopomofo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do point out spelling errors in symbol names such as those of variables, classes, methods, and functions.' in text, "expected to find: " + '- Do point out spelling errors in symbol names such as those of variables, classes, methods, and functions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Pay attention when strings cross language boundaries, especially if code point counts are involved.' in text, "expected to find: " + '- Pay attention when strings cross language boundaries, especially if code point counts are involved.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do point out style issues such as extraneous spaces (for example `a  = b;`).' in text, "expected to find: " + '- Do point out style issues such as extraneous spaces (for example `a  = b;`).'[:80]

