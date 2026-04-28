"""Behavioral checks for slint-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/slint")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`lsp/` (LSP server), `compiler/` (CLI), `viewer/` (hot-reload `.slint` viewer), `slintpad/` (web playground), `figma_import/`, `tr-extractor/` (i18n), `updater/` (version migration).' in text, "expected to find: " + '`lsp/` (LSP server), `compiler/` (CLI), `viewer/` (hot-reload `.slint` viewer), `slintpad/` (web playground), `figma_import/`, `tr-extractor/` (i18n), `updater/` (version migration).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Rust (`rs/slint/`, `rs/macros/` for `slint!`, `rs/build/`), C++ (`cpp/`, CMake), Node.js (`node/`, Neon), Python (`python/`, PyO3), WebAssembly (`wasm-interpreter/`).' in text, "expected to find: " + 'Rust (`rs/slint/`, `rs/macros/` for `slint!`, `rs/build/`), C++ (`cpp/`, CMake), Node.js (`node/`, Neon), Python (`python/`, PyO3), WebAssembly (`wasm-interpreter/`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `property-binding-deep-dive.md` — `internal/core/properties.rs`, binding bugs: reactivity, dependency tracking, two-way bindings, PropertyTracker, ChangeTracker.' in text, "expected to find: " + '- `property-binding-deep-dive.md` — `internal/core/properties.rs`, binding bugs: reactivity, dependency tracking, two-way bindings, PropertyTracker, ChangeTracker.'[:80]

