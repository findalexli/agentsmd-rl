"""Behavioral checks for xmlui-docs-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xmlui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The app is served as static files. The XMLUI runtime (`xmlui-standalone.umd.js`) is loaded via a `<script>` tag. On startup it fetches `Main.xmlui`, discovers referenced components from the `component' in text, "expected to find: " + 'The app is served as static files. The XMLUI runtime (`xmlui-standalone.umd.js`) is loaded via a `<script>` tag. On startup it fetches `Main.xmlui`, discovers referenced components from the `component'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The app uses Vite + the `vite-xmlui-plugin`. `.xmlui` files are compiled at build time into JS modules. `import.meta.glob()` in the entry point pre-bundles all components. The result is an optimized p' in text, "expected to find: " + 'The app uses Vite + the `vite-xmlui-plugin`. `.xmlui` files are compiled at build time into JS modules. `import.meta.glob()` in the entry point pre-bundles all components. The result is an optimized p'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'XMLUI is a **declarative, reactive frontend framework** for building web applications using XML markup. Users write `.xmlui` files instead of JavaScript/JSX. The framework is fully reactive — expressi' in text, "expected to find: " + 'XMLUI is a **declarative, reactive frontend framework** for building web applications using XML markup. Users write `.xmlui` files instead of JavaScript/JSX. The framework is fully reactive — expressi'[:80]

