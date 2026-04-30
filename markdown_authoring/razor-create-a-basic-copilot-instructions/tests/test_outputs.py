"""Behavioral checks for razor-create-a-basic-copilot-instructions (markdown_authoring task).

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
    assert 'This repository contains the **ASP.NET Core Razor** compiler and tooling implementation. It provides the Razor language experience across Visual Studio, Visual Studio Code, and other development envir' in text, "expected to find: " + 'This repository contains the **ASP.NET Core Razor** compiler and tooling implementation. It provides the Razor language experience across Visual Studio, Visual Studio Code, and other development envir'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| **Visual Studio** | VS-specific tooling and integration | `Microsoft.VisualStudio.RazorExtension`, `Microsoft.VisualStudio.LanguageServices.Razor` |' in text, "expected to find: " + '| **Visual Studio** | VS-specific tooling and integration | `Microsoft.VisualStudio.RazorExtension`, `Microsoft.VisualStudio.LanguageServices.Razor` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| **Compiler** | Core Razor compilation and code generation | `Microsoft.AspNetCore.Razor.Language`, `Microsoft.CodeAnalysis.Razor.Compiler` |' in text, "expected to find: " + '| **Compiler** | Core Razor compilation and code generation | `Microsoft.AspNetCore.Razor.Language`, `Microsoft.CodeAnalysis.Razor.Compiler` |'[:80]

