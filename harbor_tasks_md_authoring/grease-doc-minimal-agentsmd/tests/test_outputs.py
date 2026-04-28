"""Behavioral checks for grease-doc-minimal-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/grease")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'GREASE is a Haskell library and command-line tool for under-constrained symbolic' in text, "expected to find: " + 'GREASE is a Haskell library and command-line tool for under-constrained symbolic'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Read error handling documentation at `doc/dev/errors.md`.' in text, "expected to find: " + 'Read error handling documentation at `doc/dev/errors.md`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Test: `cd grease-exe && cabal run test:grease-tests`' in text, "expected to find: " + '- Test: `cd grease-exe && cabal run test:grease-tests`'[:80]

