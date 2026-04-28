"""Behavioral checks for adbutils-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/adbutils")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'adbutils is a pure Python library for Android Debug Bridge (ADB) operations. It provides both a Python API and command-line interface for device management, shell commands, file transfer, and Android ' in text, "expected to find: " + 'adbutils is a pure Python library for Android Debug Bridge (ADB) operations. It provides both a Python API and command-line interface for device management, shell commands, file transfer, and Android '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**ALWAYS reference these instructions first and follow them precisely. Only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in' in text, "expected to find: " + '**ALWAYS reference these instructions first and follow them precisely. Only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Import Test**: `python -c "import adbutils; adb = adbutils.AdbClient(); print(\'Success\')"` -- verify basic functionality' in text, "expected to find: " + '- **Import Test**: `python -c "import adbutils; adb = adbutils.AdbClient(); print(\'Success\')"` -- verify basic functionality'[:80]

