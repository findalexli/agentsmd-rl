"""Behavioral checks for remill-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/remill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Remill is a static binary translator that lifts machine code instructions into LLVM bitcode. It supports x86/amd64 (including AVX/AVX512), AArch64, AArch32, SPARC32/64, and PPC architectures. Remill i' in text, "expected to find: " + 'Remill is a static binary translator that lifts machine code instructions into LLVM bitcode. It supports x86/amd64 (including AVX/AVX512), AArch64, AArch32, SPARC32/64, and PPC architectures. Remill i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Intrinsics System**: Remill defers memory/control-flow semantics to downstream consumers via intrinsics (`__remill_read_memory_*`, `__remill_write_memory_*`, etc.). This allows tools to implement th' in text, "expected to find: " + '**Intrinsics System**: Remill defers memory/control-flow semantics to downstream consumers via intrinsics (`__remill_read_memory_*`, `__remill_write_memory_*`, etc.). This allows tools to implement th'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Basic Block Lifting**: Core function `__remill_basic_block(State&, addr_t, Memory*)` - variables correspond to register names, decoder and lifter synchronize via this naming convention.' in text, "expected to find: " + '**Basic Block Lifting**: Core function `__remill_basic_block(State&, addr_t, Memory*)` - variables correspond to register names, decoder and lifter synchronize via this naming convention.'[:80]

