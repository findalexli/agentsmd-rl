"""Behavioral checks for mapsui-create-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mapsui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Source generator (`Mapsui.Sample.SourceGenerator`)** – Scans all classes that implement `ISample`, `ISampleBase`, `ISampleTest`, or `IMapViewSample` at build time and generates a `Samples.Register' in text, "expected to find: " + '- **Source generator (`Mapsui.Sample.SourceGenerator`)** – Scans all classes that implement `ISample`, `ISampleBase`, `ISampleTest`, or `IMapViewSample` at build time and generates a `Samples.Register'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Sample projects** – Under `Samples`. They reference the appropriate UI wrapper and demonstrate usage. They are built only for demonstration and are not required for library consumption.' in text, "expected to find: " + '- **Sample projects** – Under `Samples`. They reference the appropriate UI wrapper and demonstrate usage. They are built only for demonstration and are not required for library consumption.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **UI wrappers** – Separate projects for each UI framework (e.g., `Mapsui.UI.Maui`, `Mapsui.UI.Wpf`, `Mapsui.UI.Blazor`). Each exposes a `MapControl` that hosts a `Map` instance.' in text, "expected to find: " + '- **UI wrappers** – Separate projects for each UI framework (e.g., `Mapsui.UI.Maui`, `Mapsui.UI.Wpf`, `Mapsui.UI.Blazor`). Each exposes a `MapControl` that hosts a `Map` instance.'[:80]

