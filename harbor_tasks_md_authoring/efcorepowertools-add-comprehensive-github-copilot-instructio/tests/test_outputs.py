"""Behavioral checks for efcorepowertools-add-comprehensive-github-copilot-instructio (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/efcorepowertools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'EF Core Power Tools is a comprehensive toolkit for Entity Framework Core development consisting of a Visual Studio extension (VSIX), command-line tools (CLI), and supporting libraries. It enables reve' in text, "expected to find: " + 'EF Core Power Tools is a comprehensive toolkit for Entity Framework Core development consisting of a Visual Studio extension (VSIX), command-line tools (CLI), and supporting libraries. It enables reve'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'cp /home/runner/work/EFCorePowerTools/EFCorePowerTools/test/ScaffoldingTester/Chinook/obj/Debug/netstandard2.1/ErikEJ.Dacpac.Chinook.dacpac .' in text, "expected to find: " + 'cp /home/runner/work/EFCorePowerTools/EFCorePowerTools/test/ScaffoldingTester/Chinook/obj/Debug/netstandard2.1/ErikEJ.Dacpac.Chinook.dacpac .'[:80]

