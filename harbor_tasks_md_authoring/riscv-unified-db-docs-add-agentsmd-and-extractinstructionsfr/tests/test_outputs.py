"""Behavioral checks for riscv-unified-db-docs-add-agentsmd-and-extractinstructionsfr (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/riscv-unified-db")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/extract-instructions-from-subsection/SKILL.md')
    assert 'Extract all RISC-V instruction names mentioned in the specified subsection of the given AsciiDoc file, then write them to `/tmp/<subsection-title>.yaml`, where `<subsection-title>` is argument 1 lower' in text, "expected to find: " + 'Extract all RISC-V instruction names mentioned in the specified subsection of the given AsciiDoc file, then write them to `/tmp/<subsection-title>.yaml`, where `<subsection-title>` is argument 1 lower'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/extract-instructions-from-subsection/SKILL.md')
    assert 'Any token introduced by "pseudoinstruction" (with or without "assembler") must be excluded, even if it appears elsewhere in the subsection outside a pseudoinstruction context. Collect all pseudoinstru' in text, "expected to find: " + 'Any token introduced by "pseudoinstruction" (with or without "assembler") must be excluded, even if it appears elsewhere in the subsection outside a pseudoinstruction context. Collect all pseudoinstru'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/extract-instructions-from-subsection/SKILL.md')
    assert 'Derive the output filename from argument 1: lowercase it and replace spaces with hyphens (e.g., `"Multiplication Operations"` → `multiplication-operations`). Write `/tmp/<derived-name>.yaml` with the ' in text, "expected to find: " + 'Derive the output filename from argument 1: lowercase it and replace spaces with hyphens (e.g., `"Multiplication Operations"` → `multiplication-operations`). Write `/tmp/<derived-name>.yaml` with the '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The RISC-V Unified Database (UnifiedDB/UDB) is a repository that holds all information needed to describe RISC-V: extensions, instructions, CSRs, profiles, and documentation prose. Tools generate arti' in text, "expected to find: " + 'The RISC-V Unified Database (UnifiedDB/UDB) is a repository that holds all information needed to describe RISC-V: extensions, instructions, CSRs, profiles, and documentation prose. Tools generate arti'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'IDL is compiled by the `idlc` gem. The compiler performs type checking and can generate AsciiDoc documentation, option analysis, and other passes. Key types: `Bits<N>`, `XReg` (alias for `Bits<MXLEN>`' in text, "expected to find: " + 'IDL is compiled by the `idlc` gem. The compiler performs type checking and can generate AsciiDoc documentation, option analysis, and other passes. Key types: `Bits<N>`, `XReg` (alias for `Bits<MXLEN>`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `Udb::Resolver` class is the entry point: `resolver.cfg_arch_for("rv64")` returns an `Architecture` object. The `Architecture` class provides methods like `extensions()`, `instructions()`, `csrs()' in text, "expected to find: " + 'The `Udb::Resolver` class is the entry point: `resolver.cfg_arch_for("rv64")` returns an `Architecture` object. The `Architecture` class provides methods like `extensions()`, `instructions()`, `csrs()'[:80]

