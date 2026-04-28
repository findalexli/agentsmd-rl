"""Behavioral checks for lox-docs-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Lox is a safe, ergonomic Rust astrodynamics library with Python bindings (via PyO3/maturin). It provides high-precision time systems, reference frame transformations, orbital mechanics, ground station' in text, "expected to find: " + 'Lox is a safe, ergonomic Rust astrodynamics library with Python bindings (via PyO3/maturin). It provides high-precision time systems, reference frame transformations, orbital mechanics, ground station'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Time representation**: `Time<T: TimeScale>` with femtosecond precision (i64 seconds + attoseconds). Continuous time scales are the default; leap seconds are handled strictly at the UTC I/O boundar' in text, "expected to find: " + '- **Time representation**: `Time<T: TimeScale>` with femtosecond precision (i64 seconds + attoseconds). Continuous time scales are the default; leap seconds are handled strictly at the UTC I/O boundar'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Frame transformations**: Matrix-based rotation pipelines. Transformation chains: ICRF <-> J2000, and CIO-based (CIRF -> TIRF -> ITRF) or equinox-based (MOD -> TOD -> PEF) paths.' in text, "expected to find: " + '- **Frame transformations**: Matrix-based rotation pipelines. Transformation chains: ICRF <-> J2000, and CIO-based (CIRF -> TIRF -> ITRF) or equinox-based (MOD -> TOD -> PEF) paths.'[:80]

