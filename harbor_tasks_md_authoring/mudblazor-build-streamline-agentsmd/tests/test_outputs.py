"""Behavioral checks for mudblazor-build-streamline-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mudblazor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '8. **Forgetting to run `dotnet format`** - MUST run `dotnet format src/MudBlazor.slnx` before finalizing changes' in text, "expected to find: " + '8. **Forgetting to run `dotnet format`** - MUST run `dotnet format src/MudBlazor.slnx` before finalizing changes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always check initial state by running the Build and Test sequence (skip Clean unless needed).' in text, "expected to find: " + '- Always check initial state by running the Build and Test sequence (skip Clean unless needed).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'dotnet pack src/MudBlazor/MudBlazor.csproj -c Release -o ./LocalNuGet -p:Version=8.0.0-custom' in text, "expected to find: " + 'dotnet pack src/MudBlazor/MudBlazor.csproj -c Release -o ./LocalNuGet -p:Version=8.0.0-custom'[:80]

