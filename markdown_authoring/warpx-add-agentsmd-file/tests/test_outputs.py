"""Behavioral checks for warpx-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/warpx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'In `.cpp` files: (1) corresponding header, (2) WarpX headers, (3) WarpX forward declarations, (4) AMReX headers, (5) AMReX forward declarations, (6) third-party headers, (7) standard library. Each gro' in text, "expected to find: " + 'In `.cpp` files: (1) corresponding header, (2) WarpX headers, (3) WarpX forward declarations, (4) AMReX headers, (5) AMReX forward declarations, (6) third-party headers, (7) standard library. Each gro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'WarpX is a massively parallel electromagnetic Particle-In-Cell (PIC) code built on top of AMReX (adaptive mesh refinement framework). It supports multiple dimensionalities (1D, 2D, 3D, RZ cylindrical)' in text, "expected to find: " + 'WarpX is a massively parallel electromagnetic Particle-In-Cell (PIC) code built on top of AMReX (adaptive mesh refinement framework). It supports multiple dimensionalities (1D, 2D, 3D, RZ cylindrical)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When debugging/fixing tests: do not modify the tolerance of assert statements in the Python analysis files just to make the tests pass (unless explicitly asked to do so).' in text, "expected to find: " + '- When debugging/fixing tests: do not modify the tolerance of assert statements in the Python analysis files just to make the tests pass (unless explicitly asked to do so).'[:80]

