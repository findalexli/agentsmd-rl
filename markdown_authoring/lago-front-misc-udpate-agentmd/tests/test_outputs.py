"""Behavioral checks for lago-front-misc-udpate-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lago-front")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'const role = isAdmin ? (isManager ? "Manager" : "Admin") : "User";' in text, "expected to find: " + 'const role = isAdmin ? (isManager ? "Manager" : "Admin") : "User";'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Extract any logic above, when it starts to be complex.' in text, "expected to find: " + 'Extract any logic above, when it starts to be complex.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '{score > 80 ? "High" : score > 50 ? "Medium" : "Low"}' in text, "expected to find: " + '{score > 80 ? "High" : score > 50 ? "Medium" : "Low"}'[:80]

