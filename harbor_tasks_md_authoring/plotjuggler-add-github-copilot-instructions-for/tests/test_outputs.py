"""Behavioral checks for plotjuggler-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/plotjuggler")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "PlotJuggler is a Qt-based desktop application for visualizing time series data. It's a cross-platform tool (Linux, macOS, Windows) that supports various data formats and provides real-time streaming c" in text, "expected to find: " + "PlotJuggler is a Qt-based desktop application for visualizing time series data. It's a cross-platform tool (Linux, macOS, Windows) that supports various data formats and provides real-time streaming c"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'cmake -G "Visual Studio 16" -S src/PlotJuggler -B build/PlotJuggler -DCMAKE_TOOLCHAIN_FILE=%CMAKE_TOOLCHAIN% -DCMAKE_INSTALL_PREFIX=%cd%/install -DCMAKE_POLICY_DEFAULT_CMP0091=NEW' in text, "expected to find: " + 'cmake -G "Visual Studio 16" -S src/PlotJuggler -B build/PlotJuggler -DCMAKE_TOOLCHAIN_FILE=%CMAKE_TOOLCHAIN% -DCMAKE_INSTALL_PREFIX=%cd%/install -DCMAKE_POLICY_DEFAULT_CMP0091=NEW'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'cmake -S src/PlotJuggler -B build/PlotJuggler -DCMAKE_INSTALL_PREFIX=install -DCMAKE_POLICY_VERSION_MINIMUM=3.5' in text, "expected to find: " + 'cmake -S src/PlotJuggler -B build/PlotJuggler -DCMAKE_INSTALL_PREFIX=install -DCMAKE_POLICY_VERSION_MINIMUM=3.5'[:80]

