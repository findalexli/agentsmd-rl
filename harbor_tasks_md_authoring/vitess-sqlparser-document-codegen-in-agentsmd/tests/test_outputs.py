"""Behavioral checks for vitess-sqlparser-document-codegen-in-agentsmd (markdown_authoring task).

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
    text = _read('go/vt/sqlparser/AGENTS.md')
    assert '- **Resolving merge conflicts in generated files** → resolve the *source* file conflict, then regenerate' in text, "expected to find: " + '- **Resolving merge conflicts in generated files** → resolve the *source* file conflict, then regenerate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('go/vt/sqlparser/AGENTS.md')
    assert '| `make sqlparser` | Runs `go generate ./go/vt/sqlparser/...` (parser + AST helpers + formatter) |' in text, "expected to find: " + '| `make sqlparser` | Runs `go generate ./go/vt/sqlparser/...` (parser + AST helpers + formatter) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('go/vt/sqlparser/AGENTS.md')
    assert '| `make sizegen` | Runs `sizegen` to regenerate `cached_size.go` files across the repo |' in text, "expected to find: " + '| `make sizegen` | Runs `sizegen` to regenerate `cached_size.go` files across the repo |'[:80]

