"""Behavioral checks for cockroach-logictest-add-a-claudemd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cockroach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/logictest/CLAUDE.md')
    assert 'bazel test //pkg/sql/logictest/tests/cockroach-go-testserver-25.4:cockroach-go-testserver-25_4_test \\' in text, "expected to find: " + 'bazel test //pkg/sql/logictest/tests/cockroach-go-testserver-25.4:cockroach-go-testserver-25_4_test \\'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/logictest/CLAUDE.md')
    assert '**Type characters:** `T` (text), `I` (integer), `F` (float), `R` (decimal), `B` (bool), `O` (oid)' in text, "expected to find: " + '**Type characters:** `T` (text), `I` (integer), `F` (float), `R` (decimal), `B` (bool), `O` (oid)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/logictest/CLAUDE.md')
    assert "./dev testlogic base --files='(fk|grant)'             # Multiple patterns, all default configs" in text, "expected to find: " + "./dev testlogic base --files='(fk|grant)'             # Multiple patterns, all default configs"[:80]

