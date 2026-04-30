"""Behavioral checks for winui-gallery-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/winui-gallery")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. `Samples/Data/ControlInfoData.json` defines all control entries grouped by category (Fundamentals, Design, Accessibility, etc.). Each item has `UniqueId`, `Title`, `Description`, `Docs`, `IsNew`/`I' in text, "expected to find: " + '1. `Samples/Data/ControlInfoData.json` defines all control entries grouped by category (Fundamentals, Design, Accessibility, etc.). Each item has `UniqueId`, `Title`, `Description`, `Docs`, `IsNew`/`I'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **WinUIGallery.SourceGenerator** — Incremental source generator that reads `ControlInfoData.json` at compile time and emits `SamplesNavigationPageMappings.cs` to map control IDs → page types' in text, "expected to find: " + '- **WinUIGallery.SourceGenerator** — Incremental source generator that reads `ControlInfoData.json` at compile time and emits `SamplesNavigationPageMappings.cs` to map control IDs → page types'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`ControlExample` exposes: `Example`, `Output`, `Options`, `Xaml`/`XamlSource`, `CSharp`/`CSharpSource`, and `Substitutions` for dynamic `$(Key)` replacements in displayed code.' in text, "expected to find: " + '`ControlExample` exposes: `Example`, `Output`, `Options`, `Xaml`/`XamlSource`, `CSharp`/`CSharpSource`, and `Substitutions` for dynamic `$(Key)` replacements in displayed code.'[:80]

