"""Behavioral checks for editor-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/editor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **editor-api** — `@playcanvas/editor-api` at `modules/editor-api/`, exposes `api.globals.*` (history, selection, assets, entities, realtime); `editor` global injected via Rollup footer' in text, "expected to find: " + '- **editor-api** — `@playcanvas/editor-api` at `modules/editor-api/`, exposes `api.globals.*` (history, selection, assets, entities, realtime); `editor` global injected via Rollup footer'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Side-effect imports** — `src/editor/index.ts` registers all modules on import; do not remove imports unless removing a feature' in text, "expected to find: " + '- **Side-effect imports** — `src/editor/index.ts` registers all modules on import; do not remove imports unless removing a feature'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Caller pattern** — cross-module communication via `this.call('method:name', ...args)` / `this.method('method:name', handler)`" in text, "expected to find: " + "- **Caller pattern** — cross-module communication via `this.call('method:name', ...args)` / `this.method('method:name', handler)`"[:80]

