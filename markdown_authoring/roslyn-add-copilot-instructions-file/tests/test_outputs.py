"""Behavioral checks for roslyn-add-copilot-instructions-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/roslyn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Run `dotnet format whitespace -f . --include ` followed by the relative paths to changed .cs and .vb files to apply formatting preferences' in text, "expected to find: " + '- Run `dotnet format whitespace -f . --include ` followed by the relative paths to changed .cs and .vb files to apply formatting preferences'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Compilers** (`src/Compilers/`): C# and VB.NET compilers with syntax trees, semantic models, symbols, and emit APIs' in text, "expected to find: " + '- **Compilers** (`src/Compilers/`): C# and VB.NET compilers with syntax trees, semantic models, symbols, and emit APIs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Run `dotnet msbuild <path to csproj> /t:UpdateXlf` when .resx files are modified to update corresponding .xlf files' in text, "expected to find: " + '- Run `dotnet msbuild <path to csproj> /t:UpdateXlf` when .resx files are modified to update corresponding .xlf files'[:80]

