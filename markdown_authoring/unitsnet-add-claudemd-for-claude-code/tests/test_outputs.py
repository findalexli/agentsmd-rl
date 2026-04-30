"""Behavioral checks for unitsnet-add-claudemd-for-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unitsnet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'UnitsNet is a .NET library that provides strongly-typed physical units and quantities, enabling safe and intuitive unit conversions in code. The library uses code generation from JSON definitions to c' in text, "expected to find: " + 'UnitsNet is a .NET library that provides strongly-typed physical units and quantities, enabling safe and intuitive unit conversions in code. The library uses code generation from JSON definitions to c'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Run single test**: `dotnet test UnitsNet.Tests --filter "FullyQualifiedName~TestClassName.TestMethodName"`' in text, "expected to find: " + '- **Run single test**: `dotnet test UnitsNet.Tests --filter "FullyQualifiedName~TestClassName.TestMethodName"`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]

