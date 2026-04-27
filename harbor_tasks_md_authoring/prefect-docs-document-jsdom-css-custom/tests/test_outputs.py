"""Behavioral checks for prefect-docs-document-jsdom-css-custom (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '- **CSS custom properties**: JSDOM does not load external stylesheets, so `getComputedStyle` returns `""` for CSS custom properties (e.g., Tailwind breakpoint tokens like `--breakpoint-lg`). Mock them' in text, "expected to find: " + '- **CSS custom properties**: JSDOM does not load external stylesheets, so `getComputedStyle` returns `""` for CSS custom properties (e.g., Tailwind breakpoint tokens like `--breakpoint-lg`). Mock them'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '- **`matchMedia` mocking**: JSDOM does not implement `window.matchMedia`. Stub it via `Object.defineProperty(window, "matchMedia", ...)` and restore the original in `afterEach`.' in text, "expected to find: " + '- **`matchMedia` mocking**: JSDOM does not implement `window.matchMedia`. Stub it via `Object.defineProperty(window, "matchMedia", ...)` and restore the original in `afterEach`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '.mockImplementation((name) => name === "--breakpoint-lg" ? "64rem" : "");' in text, "expected to find: " + '.mockImplementation((name) => name === "--breakpoint-lg" ? "64rem" : "");'[:80]

