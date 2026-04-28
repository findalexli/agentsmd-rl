"""Behavioral checks for android-libraries-copilot-updatesimplify-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/android-libraries")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Creates .NET for Android bindings for Google\'s Java/Kotlin libraries (AndroidX, Play Services, Firebase, ML Kit, etc.) using a **config-driven approach** with `config.json` and the "binderator" tool.' in text, "expected to find: " + 'Creates .NET for Android bindings for Google\'s Java/Kotlin libraries (AndroidX, Play Services, Firebase, ML Kit, etc.) using a **config-driven approach** with `config.json` and the "binderator" tool.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **`config.json`**: Master config for 600+ Maven artifacts → NuGet packages. Update via `dotnet cake --target=update-config` or `bump-config`, not manually.' in text, "expected to find: " + '- **`config.json`**: Master config for 600+ Maven artifacts → NuGet packages. Update via `dotnet cake --target=update-config` or `bump-config`, not manually.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Transient parallel build issue. Usually resolves on retry. If persistent, may need to reduce build parallelism in `build/cake/build-and-package.cake`.' in text, "expected to find: " + 'Transient parallel build issue. Usually resolves on retry. If persistent, may need to reduce build parallelism in `build/cake/build-and-package.cake`.'[:80]

