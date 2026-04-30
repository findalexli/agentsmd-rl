"""Behavioral checks for swc-docs-move-parser-design-guidance (markdown_authoring task).

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
    text = _read('crates/swc_es_parser/AGENTS.md')
    assert '- The suite mirrors `swc_ecma_parser` fixture skip rules for `typescript/tsc` and `test262` pass ignores.' in text, "expected to find: " + '- The suite mirrors `swc_ecma_parser` fixture skip rules for `typescript/tsc` and `test262` pass ignores.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_parser/AGENTS.md')
    assert '- A parity fixture mode can classify known shared fixtures as expected success or expected failure.' in text, "expected to find: " + '- A parity fixture mode can classify known shared fixtures as expected success or expected failure.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/swc_es_parser/AGENTS.md')
    assert '- `swc_es_parser/tests/parity_suite.rs` reuses the `swc_ecma_parser/tests` fixture corpus.' in text, "expected to find: " + '- `swc_es_parser/tests/parity_suite.rs` reuses the `swc_ecma_parser/tests` fixture corpus.'[:80]

