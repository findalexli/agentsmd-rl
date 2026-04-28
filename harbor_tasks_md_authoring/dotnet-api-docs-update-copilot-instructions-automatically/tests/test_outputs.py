"""Behavioral checks for dotnet-api-docs-update-copilot-instructions-automatically (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-api-docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repo contains the official .NET API reference documentation in ECMAXML format. The `xml/` directory holds one XML file per type, organized by namespace (e.g., `xml/System/String.xml`). Documentat' in text, "expected to find: " + 'This repo contains the official .NET API reference documentation in ECMAXML format. The `xml/` directory holds one XML file per type, organized by namespace (e.g., `xml/System/String.xml`). Documentat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Some namespaces (notably `Microsoft.Extensions.*`, `System.CommandLine.*`, `System.Formats.*`, `System.Numerics.Tensors.*`) are auto-generated from source code in other repos. Their `open_to_public_co' in text, "expected to find: " + 'Some namespaces (notably `Microsoft.Extensions.*`, `System.CommandLine.*`, `System.Formats.*`, `System.Numerics.Tensors.*`) are auto-generated from source code in other repos. Their `open_to_public_co'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Don't escape backticks or asterisks in xref DocIDs. Use literal `` ` `` and `*` characters, not URL-encoded forms like `%60` or `%2A`. For example, use `` <xref:System.Collections.Generic.List`1> ``, " in text, "expected to find: " + "Don't escape backticks or asterisks in xref DocIDs. Use literal `` ` `` and `*` characters, not URL-encoded forms like `%60` or `%2A`. For example, use `` <xref:System.Collections.Generic.List`1> ``, "[:80]

