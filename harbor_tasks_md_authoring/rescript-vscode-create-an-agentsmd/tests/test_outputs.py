"""Behavioral checks for rescript-vscode-create-an-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rescript-vscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- As mentioned above the native OCaml binaries here are only here for backwards-compatibility with ReScript versions 11 or below. Since ReScript 12 both `analysis` and `tools` are part of the [ReScrip' in text, "expected to find: " + '- As mentioned above the native OCaml binaries here are only here for backwards-compatibility with ReScript versions 11 or below. Since ReScript 12 both `analysis` and `tools` are part of the [ReScrip'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the official ReScript VSCode extension, providing language support for ReScript (.res/.resi files) in Visual Studio Code. The project uses a Language Server Protocol (LSP) architecture with a ' in text, "expected to find: " + 'This is the official ReScript VSCode extension, providing language support for ReScript (.res/.resi files) in Visual Studio Code. The project uses a Language Server Protocol (LSP) architecture with a '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **analysis/**: Native OCaml binary for code analysis, hover, autocomplete, and other language features. This is for older ReScript versions only (ReScript 11 and below). New features are usually onl' in text, "expected to find: " + '- **analysis/**: Native OCaml binary for code analysis, hover, autocomplete, and other language features. This is for older ReScript versions only (ReScript 11 and below). New features are usually onl'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

