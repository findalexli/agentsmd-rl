"""Behavioral checks for pareto-mac-update-claude-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pareto-mac")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `debug` - Output detailed check status (supports `?check=<checkname>` parameter)' in text, "expected to find: " + '- `debug` - Output detailed check status (supports `?check=<checkname>` parameter)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `enrollTeam` - Enroll device to team (not available in SetApp build)' in text, "expected to find: " + '- `enrollTeam` - Enroll device to team (not available in SetApp build)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `update` - Force update check (not available in SetApp build)' in text, "expected to find: " + '- `update` - Force update check (not available in SetApp build)'[:80]

