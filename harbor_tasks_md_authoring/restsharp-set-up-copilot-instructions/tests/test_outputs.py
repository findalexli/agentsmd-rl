"""Behavioral checks for restsharp-set-up-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/restsharp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Package versions are centrally managed in `Directory.Packages.props`. Do not pin versions in individual projects unless justified by TFM constraints.' in text, "expected to find: " + 'Package versions are centrally managed in `Directory.Packages.props`. Do not pin versions in individual projects unless justified by TFM constraints.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'dotnet test test/RestSharp.Tests/RestSharp.Tests.csproj --filter "FullyQualifiedName=Namespace.Class.Method" -f net8.0' in text, "expected to find: " + 'dotnet test test/RestSharp.Tests/RestSharp.Tests.csproj --filter "FullyQualifiedName=Namespace.Class.Method" -f net8.0'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'dotnet pack src/RestSharp/RestSharp.csproj -c Release -o nuget -p:IncludeSymbols=true -p:SymbolPackageFormat=snupkg' in text, "expected to find: " + 'dotnet pack src/RestSharp/RestSharp.csproj -c Release -o nuget -p:IncludeSymbols=true -p:SymbolPackageFormat=snupkg'[:80]

