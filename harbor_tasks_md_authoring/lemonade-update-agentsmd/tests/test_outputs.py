"""Behavioral checks for lemonade-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lemonade")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Integration tests in Python against a live server. Tests auto-discover the server binary from the build directory; use `--server-binary` to override.' in text, "expected to find: " + 'Integration tests in Python against a live server. Tests auto-discover the server binary from the build directory; use `--server-binary` to override.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'CMakeLists.txt is at the repository root. Build uses CMake presets — run the setup script first, then build with `--preset`.' in text, "expected to find: " + 'CMakeLists.txt is at the repository root. Build uses CMake presets — run the setup script first, then build with `--preset`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'CMake presets: `default` (Ninja, Release), `windows` (VS 2022), `vs18` (VS 2026), `debug` (Ninja, Debug).' in text, "expected to find: " + 'CMake presets: `default` (Ninja, Release), `windows` (VS 2022), `vs18` (VS 2026), `debug` (Ninja, Debug).'[:80]

