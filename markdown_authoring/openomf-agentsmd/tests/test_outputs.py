"""Behavioral checks for openomf-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openomf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Game Description**: One Must Fall is a fighting game where two giant robots (called **HARs** - Human Assisted Robots) battle each other in various arenas. Each HAR has its own stats (arm power, leg ' in text, "expected to find: " + '**Game Description**: One Must Fall is a fighting game where two giant robots (called **HARs** - Human Assisted Robots) battle each other in various arenas. Each HAR has its own stats (arm power, leg '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'OpenOMF is an open-source remake of "One Must Fall 2097" by Diversions Entertainment. This is a **C99 project** that uses **CMake** as its build system. The project recreates a DOS fighting game from ' in text, "expected to find: " + 'OpenOMF is an open-source remake of "One Must Fall 2097" by Diversions Entertainment. This is a **C99 project** that uses **CMake** as its build system. The project recreates a DOS fighting game from '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Important**: Always build in a subdirectory (like `build/`) to avoid littering the project root with build artifacts. The project `.gitignore` is configured for this workflow.' in text, "expected to find: " + '**Important**: Always build in a subdirectory (like `build/`) to avoid littering the project root with build artifacts. The project `.gitignore` is configured for this workflow.'[:80]

