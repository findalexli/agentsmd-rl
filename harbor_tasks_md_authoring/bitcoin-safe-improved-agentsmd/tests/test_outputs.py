"""Behavioral checks for bitcoin-safe-improved-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bitcoin-safe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- take every change you do as an opportunity to improve architecture: think about if the change does introduce or remove coupling and what architecture improvements this could be used for' in text, "expected to find: " + '- take every change you do as an opportunity to improve architecture: think about if the change does introduce or remove coupling and what architecture improvements this could be used for'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- do not use someenum(str, Enum),  but instead use someenum(Enum), then (de)serailization works type safe via BaseSaveableClass' in text, "expected to find: " + '- do not use someenum(str, Enum),  but instead use someenum(Enum), then (de)serailization works type safe via BaseSaveableClass'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- do not use Callable arguments if possible' in text, "expected to find: " + '- do not use Callable arguments if possible'[:80]

