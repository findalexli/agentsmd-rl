"""Behavioral checks for bombadil-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bombadil")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Bombadil is a property-based testing tool for web UIs built by Antithesis. Users write specifications as TypeScript modules exporting LTL (Linear Temporal Logic) properties. Bombadil autonomously expl' in text, "expected to find: " + 'Bombadil is a property-based testing tool for web UIs built by Antithesis. Users write specifications as TypeScript modules exporting LTL (Linear Temporal Logic) properties. Bombadil autonomously expl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **browser** (`src/browser/`) - Chromium control via CDP (`chromiumoxide`). `state.rs` defines `BrowserState` snapshots (URL, title, console, exceptions, DOM). `actions.rs` defines `BrowserAction` (C' in text, "expected to find: " + '- **browser** (`src/browser/`) - Chromium control via CDP (`chromiumoxide`). `state.rs` defines `BrowserState` snapshots (URL, title, console, exceptions, DOM). `actions.rs` defines `BrowserAction` (C'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Integration tests are in `tests/`. Each test scenario has an HTML fixture directory (e.g., `tests/links/`, `tests/console-error/`). Tests spawn local web servers (axum) and run Bombadil against them. ' in text, "expected to find: " + 'Integration tests are in `tests/`. Each test scenario has an HTML fixture directory (e.g., `tests/links/`, `tests/console-error/`). Tests spawn local web servers (axum) and run Bombadil against them. '[:80]

