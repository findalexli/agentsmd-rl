"""Behavioral checks for cytoscape.js-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cytoscape.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If you want to read the documentation, you can grep `documentation/docmaker.json`, which contains all the documentation data (and API in JSON format).  You can search for things like "cy.on" for the' in text, "expected to find: " + '- If you want to read the documentation, you can grep `documentation/docmaker.json`, which contains all the documentation data (and API in JSON format).  You can search for things like "cy.on" for the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Library source of truth is in `src/`. Documentation source lives in `documentation/md/`, `documentation/demos/`, and `documentation/docmaker.json`. Built artifacts in `build/`, `dist/`, and generate' in text, "expected to find: " + '- Library source of truth is in `src/`. Documentation source lives in `documentation/md/`, `documentation/demos/`, and `documentation/docmaker.json`. Built artifacts in `build/`, `dist/`, and generate'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. For renderer, gesture, or grab-state changes, verify behaviour in `debug/` because visual regressions are not always caught by Mocha alone.  You need to control a browser instance to use this and y' in text, "expected to find: " + '5. For renderer, gesture, or grab-state changes, verify behaviour in `debug/` because visual regressions are not always caught by Mocha alone.  You need to control a browser instance to use this and y'[:80]

