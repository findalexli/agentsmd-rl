"""Behavioral checks for dotnet-monitor-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-monitor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`dotnet-monitor` is a diagnostic tool for capturing diagnostic artifacts from .NET applications in an operator-driven or automated manner. It provides a unified HTTP API for collecting diagnostics reg' in text, "expected to find: " + '`dotnet-monitor` is a diagnostic tool for capturing diagnostic artifacts from .NET applications in an operator-driven or automated manner. It provides a unified HTTP API for collecting diagnostics reg'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '6. **Learning Paths:** Guidance for developers on the various components in `dotnet-monitor`. It may need to be updated based on product changes.' in text, "expected to find: " + '6. **Learning Paths:** Guidance for developers on the various components in `dotnet-monitor`. It may need to be updated based on product changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Authentication:** dotnet-monitor supports API Key authentication (recommended) and Windows authentication' in text, "expected to find: " + '1. **Authentication:** dotnet-monitor supports API Key authentication (recommended) and Windows authentication'[:80]

