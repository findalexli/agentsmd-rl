"""Behavioral checks for fcitx5-mcbopomofo-set-up-instructions-for-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fcitx5-mcbopomofo")


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
    assert '- Do point out issues surrounding C++ `auto` uses. Suggest when `const auto&` can be used, for example.' in text, "expected to find: " + '- Do point out issues surrounding C++ `auto` uses. Suggest when `const auto&` can be used, for example.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do point out style issues such as extraneous spaces (for example `a  = b;`).' in text, "expected to find: " + '- Do point out style issues such as extraneous spaces (for example `a  = b;`).'[:80]

