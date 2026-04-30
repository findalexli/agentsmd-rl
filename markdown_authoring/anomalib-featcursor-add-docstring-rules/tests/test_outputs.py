"""Behavioral checks for anomalib-featcursor-add-docstring-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anomalib")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python_docstrings.mdc')
    assert 'You are an expert Python developer who writes high-quality, Google-style docstrings.' in text, "expected to find: " + 'You are an expert Python developer who writes high-quality, Google-style docstrings.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python_docstrings.mdc')
    assert '1.  **Short Description:** A concise summary of the function, class, or module.' in text, "expected to find: " + '1.  **Short Description:** A concise summary of the function, class, or module.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python_docstrings.mdc')
    assert '2.  **Longer Explanation:** (Optional) detailed description of the behavior.' in text, "expected to find: " + '2.  **Longer Explanation:** (Optional) detailed description of the behavior.'[:80]

