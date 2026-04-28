"""Behavioral checks for openroad-flow-scripts-doc-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openroad-flow-scripts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The OpenROAD (OR) engine source resides in `tools/OpenROAD/` (git submodule). For C++/Tcl development, refer to `tools/OpenROAD/AGENTS.md`.' in text, "expected to find: " + 'The OpenROAD (OR) engine source resides in `tools/OpenROAD/` (git submodule). For C++/Tcl development, refer to `tools/OpenROAD/AGENTS.md`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '# OpenROAD-flow-scripts (ORFS) agent context' in text, "expected to find: " + '# OpenROAD-flow-scripts (ORFS) agent context'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See `README.md` for the general ORFS guide.' in text, "expected to find: " + 'See `README.md` for the general ORFS guide.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

