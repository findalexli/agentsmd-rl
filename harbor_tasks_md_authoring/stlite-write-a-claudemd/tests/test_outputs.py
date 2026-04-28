"""Behavioral checks for stlite-write-a-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stlite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Stlite** is a serverless Streamlit implementation that runs entirely in web browsers using Pyodide (Python compiled to WebAssembly). It enables Python data apps to run without backend servers, makin' in text, "expected to find: " + '**Stlite** is a serverless Streamlit implementation that runs entirely in web browsers using Pyodide (Python compiled to WebAssembly). It enables Python data apps to run without backend servers, makin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '<script type="module" src="https://cdn.jsdelivr.net/npm/@stlite/browser@0.93.1/build/stlite.js"></script>' in text, "expected to find: " + '<script type="module" src="https://cdn.jsdelivr.net/npm/@stlite/browser@0.93.1/build/stlite.js"></script>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@0.93.1/build/stlite.css" />' in text, "expected to find: " + '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@0.93.1/build/stlite.css" />'[:80]

