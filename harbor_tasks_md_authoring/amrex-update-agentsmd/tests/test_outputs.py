"""Behavioral checks for amrex-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/amrex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `AMREX_GPU_DEVICE`/`ParallelFor` lambdas run on the GPU, so never capture host-only pointers (e.g., `Geometry::CellSize()`, `Geometry::ProbLo()`). Take the device-safe views first—e.g., `auto const ' in text, "expected to find: " + '- `AMREX_GPU_DEVICE`/`ParallelFor` lambdas run on the GPU, so never capture host-only pointers (e.g., `Geometry::CellSize()`, `Geometry::ProbLo()`). Take the device-safe views first—e.g., `auto const '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **GNUmakefile workflows**: When a directory ships a `GNUmakefile`, `cd` there and run `make -j` with required variables (e.g., `DIM`, `USE_MPI`, `USE_CUDA`, `COMP`) as documented in `Docs/sphinx_doc' in text, "expected to find: " + '- **GNUmakefile workflows**: When a directory ships a `GNUmakefile`, `cd` there and run `make -j` with required variables (e.g., `DIM`, `USE_MPI`, `USE_CUDA`, `COMP`) as documented in `Docs/sphinx_doc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `Src/` – Core C++/Fortran implementation. `Amr*` manage hierarchy/regridding, `Base` hosts runtime utilities, and folders such as `Boundary`, `EB`, `LinearSolvers`, `Particle`, `FFT` contain subsyst' in text, "expected to find: " + '- `Src/` – Core C++/Fortran implementation. `Amr*` manage hierarchy/regridding, `Base` hosts runtime utilities, and folders such as `Boundary`, `EB`, `LinearSolvers`, `Particle`, `FFT` contain subsyst'[:80]

