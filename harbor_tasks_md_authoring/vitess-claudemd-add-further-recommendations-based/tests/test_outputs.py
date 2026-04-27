"""Behavioral checks for vitess-claudemd-add-further-recommendations-based (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **No naked returns in non-trivial functions** - For functions with named return values, avoid bare `return` and explicitly return all result values (very small helpers are the only exception). This ' in text, "expected to find: " + '- **No naked returns in non-trivial functions** - For functions with named return values, avoid bare `return` and explicitly return all result values (very small helpers are the only exception). This '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'To make sure tests are easy to read, we use `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/require` for assertions. Use `assert.Eventually` instead of manual `time.Sleep()` and ' in text, "expected to find: " + 'To make sure tests are easy to read, we use `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/require` for assertions. Use `assert.Eventually` instead of manual `time.Sleep()` and '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Use `vterrors`** - Prefer `vterrors` over `fmt.Errorf` or `errors` package, with an appropriate `vtrpcpb.Code` (e.g., `vtrpcpb.Code_FAILED_PRECONDITION` for unexpected input values, `vtrpcpb.Code' in text, "expected to find: " + '1. **Use `vterrors`** - Prefer `vterrors` over `fmt.Errorf` or `errors` package, with an appropriate `vtrpcpb.Code` (e.g., `vtrpcpb.Code_FAILED_PRECONDITION` for unexpected input values, `vtrpcpb.Code'[:80]

