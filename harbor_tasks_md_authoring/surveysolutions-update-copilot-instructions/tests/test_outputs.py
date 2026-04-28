"""Behavioral checks for surveysolutions-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/surveysolutions")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Survey Solutions** is a large-scale, production-grade survey management and data collection platform developed by the World Bank. The repository contains multiple .NET backend projects, two Vue 3 fr' in text, "expected to find: " + '**Survey Solutions** is a large-scale, production-grade survey management and data collection platform developed by the World Bank. The repository contains multiple .NET backend projects, two Vue 3 fr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '> **Review rule:** Never access `IUnitOfWork.Session` directly for reading domain state — use the appropriate read-side repository or service abstraction. Direct session queries are only justified whe' in text, "expected to find: " + '> **Review rule:** Never access `IUnitOfWork.Session` directly for reading domain state — use the appropriate read-side repository or service abstraction. Direct session queries are only justified whe'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Vite output files are committed:** The Vite build in `WB.UI.Frontend` writes asset-hashed filenames directly into `.cshtml` Razor templates inside `WB.UI.Headquarters.Core/Views`. These generated ' in text, "expected to find: " + '- **Vite output files are committed:** The Vite build in `WB.UI.Frontend` writes asset-hashed filenames directly into `.cshtml` Razor templates inside `WB.UI.Headquarters.Core/Views`. These generated '[:80]

