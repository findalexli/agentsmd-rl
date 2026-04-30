"""Behavioral checks for whisper-money-chore-use-caveman-on-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/whisper-money")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Drop: articles, filler (just/really/basically), pleasantries, hedging.' in text, "expected to find: " + 'Drop: articles, filler (just/really/basically), pleasantries, hedging.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.' in text, "expected to find: " + 'ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Terse like caveman. Technical substance exact. Only fluff die.' in text, "expected to find: " + 'Terse like caveman. Technical substance exact. Only fluff die.'[:80]

