"""Behavioral checks for delegatedecompiler-set-up-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/delegatedecompiler")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'DelegateDecompiler is a .NET library that decompiles delegates and method bodies to their lambda representation. It enables computed properties in LINQ queries by translating `[Computed]` attributes i' in text, "expected to find: " + 'DelegateDecompiler is a .NET library that decompiles delegates and method bodies to their lambda representation. It enables computed properties in LINQ queries by translating `[Computed]` attributes i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Ensure core unit tests pass: `src/DelegateDecompiler.Tests` and `src/DelegateDecompiler.Tests.VB` should have no failures' in text, "expected to find: " + '- Ensure core unit tests pass: `src/DelegateDecompiler.Tests` and `src/DelegateDecompiler.Tests.VB` should have no failures'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'dotnet test --no-build -c Release -f net8.0 src/DelegateDecompiler.EntityFrameworkCore6.Tests' in text, "expected to find: " + 'dotnet test --no-build -c Release -f net8.0 src/DelegateDecompiler.EntityFrameworkCore6.Tests'[:80]

