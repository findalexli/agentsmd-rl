"""Behavioral checks for openvino.genai-extend-copilot-instructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openvino.genai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "16. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead." in text, "expected to find: " + "16. Assumptions on the user's behalf aren't allowed. For example, the implementation shouldn't adjust config values silently or with a warning; it should throw an exception instead."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '9. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.' in text, "expected to find: " + '9. When initial container values are known upfront, prefer initializer-list / brace-initialization over constructing an empty container and immediately inserting values.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '6. Avoid redundant inline comments next to `OPENVINO_ASSERT()` and `OPENVINO_THROW()`; the error message argument must be clear and self-explanatory.' in text, "expected to find: " + '6. Avoid redundant inline comments next to `OPENVINO_ASSERT()` and `OPENVINO_THROW()`; the error message argument must be clear and self-explanatory.'[:80]

