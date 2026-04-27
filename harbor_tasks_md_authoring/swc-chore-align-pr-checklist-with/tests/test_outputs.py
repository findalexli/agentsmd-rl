"""Behavioral checks for swc-chore-align-pr-checklist-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   Before opening or updating a PR, always run this baseline locally.' in text, "expected to find: " + '-   Before opening or updating a PR, always run this baseline locally.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   For each touched Rust crate, run crate-level verification locally.' in text, "expected to find: " + '-   For each touched Rust crate, run crate-level verification locally.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`' in text, "expected to find: " + '-   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '-   Before opening or updating a PR, always run this baseline locally.' in text, "expected to find: " + '-   Before opening or updating a PR, always run this baseline locally.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '-   For each touched Rust crate, run crate-level verification locally.' in text, "expected to find: " + '-   For each touched Rust crate, run crate-level verification locally.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '-   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`' in text, "expected to find: " + '-   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`'[:80]

