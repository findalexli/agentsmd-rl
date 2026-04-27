"""Behavioral checks for orca-docsagents-tighten-codecomment-rule-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/orca")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Keep comments short — one or two lines. Capture only the non-obvious reason (safety constraint, compatibility shim, design-doc rule). Don't restate what the code does, narrate the mechanism, cite desi" in text, "expected to find: " + "Keep comments short — one or two lines. Capture only the non-obvious reason (safety constraint, compatibility shim, design-doc rule). Don't restate what the code does, narrate the mechanism, cite desi"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Be mindful of the user's `gh` CLI API rate limit — batch requests where possible and avoid unnecessary calls. All code, commands, and scripts must be compatible with macOS, Linux, and Windows." in text, "expected to find: " + "Be mindful of the user's `gh` CLI API rate limit — batch requests where possible and avoid unnecessary calls. All code, commands, and scripts must be compatible with macOS, Linux, and Windows."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When writing or modifying code driven by a design doc or non-obvious constraint, add a comment explaining **why** the code behaves the way it does.' in text, "expected to find: " + 'When writing or modifying code driven by a design doc or non-obvious constraint, add a comment explaining **why** the code behaves the way it does.'[:80]

