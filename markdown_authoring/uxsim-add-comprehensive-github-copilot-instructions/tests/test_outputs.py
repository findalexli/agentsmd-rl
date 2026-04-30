"""Behavioral checks for uxsim-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uxsim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'UXsim is a pure Python macroscopic and mesoscopic network traffic flow simulator for large-scale (city-scale) traffic phenomena simulation. It is designed for scientific and educational purposes with ' in text, "expected to find: " + 'UXsim is a pure Python macroscopic and mesoscopic network traffic flow simulator for large-scale (city-scale) traffic phenomena simulation. It is designed for scientific and educational purposes with '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- GUI viewer examples (`example_17en_result_GUI_viewer_*.py`, `example_18en_result_GUI_viewer_*.py`) require X11 display' in text, "expected to find: " + '- GUI viewer examples (`example_17en_result_GUI_viewer_*.py`, `example_18en_result_GUI_viewer_*.py`) require X11 display'[:80]

