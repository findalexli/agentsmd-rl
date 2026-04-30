"""Behavioral checks for caly-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caly")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Caly is a cross-platform PDF reader built with Avalonia UI and .NET. It targets Windows, Linux, macOS, Android, and iOS. The master branch uses NuGet packages; the develop branch uses git submodules i' in text, "expected to find: " + 'Caly is a cross-platform PDF reader built with Avalonia UI and .NET. It targets Windows, Linux, macOS, Android, and iOS. The master branch uses NuGet packages; the develop branch uses git submodules i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Pages are rendered to `SKPicture` (SkiaSharp, **software-only** — no GPU) by `PdfPig.Rendering.Skia`. `SkiaPdfPageControl` draws the cached `SKPicture` onto the Avalonia canvas. Thumbnails use the sam' in text, "expected to find: " + 'Pages are rendered to `SKPicture` (SkiaSharp, **software-only** — no GPU) by `PdfPig.Rendering.Skia`. `SkiaPdfPageControl` draws the cached `SKPicture` onto the Avalonia canvas. Thumbnails use the sam'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All projects target both `net9.0` and `net10.0`. Mobile targets use `net10.0-android` / `net10.0-ios`. Use `#if` guards or `<TargetFrameworks>` conditions for version-specific code.' in text, "expected to find: " + 'All projects target both `net9.0` and `net10.0`. Mobile targets use `net10.0-android` / `net10.0-ios`. Use `#if` guards or `<TargetFrameworks>` conditions for version-specific code.'[:80]

