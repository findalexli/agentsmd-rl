"""Behavioral checks for dftk.jl-add-a-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dftk.jl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**DFTK** (Density-Functional Toolkit) is a Julia library for plane-wave density-functional theory (DFT) calculations. Its emphasis is on **simplicity and flexibility** to facilitate algorithmic/numeri' in text, "expected to find: " + '**DFTK** (Density-Functional Toolkit) is a Julia library for plane-wave density-functional theory (DFT) calculations. Its emphasis is on **simplicity and flexibility** to facilitate algorithmic/numeri'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is normal. Do not assume a hang is a bug if the process has been running for under 5 minutes without output. Subsequent runs in the same Julia session will be much faster. Disabling precompilatio' in text, "expected to find: " + 'This is normal. Do not assume a hang is a bug if the process has been running for under 5 minutes without output. Subsequent runs in the same Julia session will be much faster. Disabling precompilatio'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "6. **Extensions:** GPU, I/O, and Wannier functionality only works when the corresponding Julia packages are loaded (`using CUDA`, `using JLD2`, etc.). Don't `import`/`using` them in core source files " in text, "expected to find: " + "6. **Extensions:** GPU, I/O, and Wannier functionality only works when the corresponding Julia packages are loaded (`using CUDA`, `using JLD2`, etc.). Don't `import`/`using` them in core source files "[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

