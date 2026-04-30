"""Behavioral checks for razor-simplify-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/razor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **RazorCodeDocument**: Immutable — every `With*` method creates a new instance passing ALL fields through the constructor. When adding a new field, thread it through every existing `With*` method. P' in text, "expected to find: " + '- **RazorCodeDocument**: Immutable — every `With*` method creates a new instance passing ALL fields through the constructor. When adding a new field, thread it through every existing `With*` method. P'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Test**: Use `build.cmd -test` or target a specific project with `dotnet test path/to/Project.csproj`. NEVER run `dotnet test` at the repo root — it includes Playwright integration tests that requi' in text, "expected to find: " + '- **Test**: Use `build.cmd -test` or target a specific project with `dotnet test path/to/Project.csproj`. NEVER run `dotnet test` at the repo root — it includes Playwright integration tests that requi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **LSP conversions**: `sourceText.GetTextChange(textEdit)` converts LSP `TextEdit` → Roslyn `TextChange`. Reverse: `sourceText.GetTextEdit(change)`. Both in `LspExtensions_SourceText.cs`.' in text, "expected to find: " + '- **LSP conversions**: `sourceText.GetTextChange(textEdit)` converts LSP `TextEdit` → Roslyn `TextChange`. Reverse: `sourceText.GetTextEdit(change)`. Both in `LspExtensions_SourceText.cs`.'[:80]

