"""Behavioral checks for ojp-add-agent-behavior-guidelines-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ojp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.' in text, "expected to find: " + '- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Be honest, even when the honest answer is "I don\'t know" or "this approach has problems."' in text, "expected to find: " + '- Be honest, even when the honest answer is "I don\'t know" or "this approach has problems."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- Don't default to agreement — push back when something seems wrong or suboptimal." in text, "expected to find: " + "- Don't default to agreement — push back when something seems wrong or suboptimal."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.' in text, "expected to find: " + '- Proactively offer questions, opinions, suggestions, and concerns rather than waiting to be asked.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '- Be honest, even when the honest answer is "I don\'t know" or "this approach has problems."' in text, "expected to find: " + '- Be honest, even when the honest answer is "I don\'t know" or "this approach has problems."'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert "- Don't default to agreement — push back when something seems wrong or suboptimal." in text, "expected to find: " + "- Don't default to agreement — push back when something seems wrong or suboptimal."[:80]

