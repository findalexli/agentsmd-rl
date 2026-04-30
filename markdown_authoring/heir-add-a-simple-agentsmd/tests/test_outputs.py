"""Behavioral checks for heir-add-a-simple-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/heir")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`--dump-pass-pipeline --mlir-print-ir-before-all --mlir-print-ir-tree-dir=/tmp/mlir`,' in text, "expected to find: " + '`--dump-pass-pipeline --mlir-print-ir-before-all --mlir-print-ir-tree-dir=/tmp/mlir`,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `scripts/templates/templates.py` (which requires `python-fire` and `jinja2`)' in text, "expected to find: " + '- `scripts/templates/templates.py` (which requires `python-fire` and `jinja2`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`LLVM_DEBUG` in files that have the macro `#define DEBUG_TYPE "my-tag"`. This' in text, "expected to find: " + '`LLVM_DEBUG` in files that have the macro `#define DEBUG_TYPE "my-tag"`. This'[:80]

