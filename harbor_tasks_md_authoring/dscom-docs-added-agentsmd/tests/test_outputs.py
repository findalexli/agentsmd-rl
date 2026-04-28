"""Behavioral checks for dscom-docs-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dscom")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'dscom is a .NET library and CLI tool that replaces deprecated Microsoft COM tools (`tlbexp.exe`, `OleView`, `RegAsm.exe`) for .NET 5+. It exports .NET assemblies to COM Type Libraries (TLBs), register' in text, "expected to find: " + 'dscom is a .NET library and CLI tool that replaces deprecated Microsoft COM tools (`tlbexp.exe`, `OleView`, `RegAsm.exe`) for .NET 5+. It exports .NET assemblies to COM Type Libraries (TLBs), register'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**If a breaking change is detected, the agent MUST stop and warn the user before proceeding.** The implementation may only continue after the user explicitly confirms that the breaking change is accep' in text, "expected to find: " + '**If a breaking change is detected, the agent MUST stop and warn the user before proceeding.** The implementation may only continue after the user explicitly confirms that the breaking change is accep'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Writer hierarchy**: `BaseWriter` → specialized writers (ClassWriter, InterfaceWriter, EnumWriter, StructWriter, MethodWriter, etc.). Each writer has a `Create()` method that builds and registers COM' in text, "expected to find: " + '**Writer hierarchy**: `BaseWriter` → specialized writers (ClassWriter, InterfaceWriter, EnumWriter, StructWriter, MethodWriter, etc.). Each writer has a `Create()` method that builds and registers COM'[:80]

