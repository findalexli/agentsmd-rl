"""Behavioral checks for anymap-ts-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anymap-ts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**anymap-ts** is a Python package for creating interactive maps in Jupyter notebooks using [anywidget](https://anywidget.dev/) and TypeScript. It provides a unified Python interface to multiple JavaSc' in text, "expected to find: " + '**anymap-ts** is a Python package for creating interactive maps in Jupyter notebooks using [anywidget](https://anywidget.dev/) and TypeScript. It provides a unified Python interface to multiple JavaSc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The conda-forge package is maintained separately at [conda-forge/anymap-ts-feedstock](https://github.com/conda-forge/anymap-ts-feedstock).' in text, "expected to find: " + 'The conda-forge package is maintained separately at [conda-forge/anymap-ts-feedstock](https://github.com/conda-forge/anymap-ts-feedstock).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Implement abstract methods: `initialize()`, `destroy()`, `createMap()`, `onCenterChange()`, `onZoomChange()`, `onStyleChange()`' in text, "expected to find: " + '- Implement abstract methods: `initialize()`, `destroy()`, `createMap()`, `onCenterChange()`, `onZoomChange()`, `onStyleChange()`'[:80]

