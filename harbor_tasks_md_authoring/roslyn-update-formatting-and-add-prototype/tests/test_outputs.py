"""Behavioral checks for roslyn-update-formatting-and-add-prototype (markdown_authoring task).

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
    assert '- **Namespace Strategy**: `Microsoft.CodeAnalysis.[Language].[Area]` (e.g., `Microsoft.CodeAnalysis.CSharp.Formatting`)' in text, "expected to find: " + '- **Namespace Strategy**: `Microsoft.CodeAnalysis.[Language].[Area]` (e.g., `Microsoft.CodeAnalysis.CSharp.Formatting`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **PROTOTYPE Comments**: Only used to track follow-up work in feature branches and are disallowed in main branch' in text, "expected to find: " + '- **PROTOTYPE Comments**: Only used to track follow-up work in feature branches and are disallowed in main branch'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Immutability**: All syntax trees, documents, and solutions are immutable - create new instances for changes' in text, "expected to find: " + '- **Immutability**: All syntax trees, documents, and solutions are immutable - create new instances for changes'[:80]

