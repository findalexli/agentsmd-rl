"""Behavioral checks for cadence-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cadence")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `tools/` — Go tooling plus custom linters (`maprange`, `unkeyed`, `constructorcheck`), a `golangci-lint` wrapper, `analysis`, `ast-explorer`, `compare-parsing`, `compatibility-check`, `get-contracts' in text, "expected to find: " + '- `tools/` — Go tooling plus custom linters (`maprange`, `unkeyed`, `constructorcheck`), a `golangci-lint` wrapper, `analysis`, `ast-explorer`, `compare-parsing`, `compatibility-check`, `get-contracts'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Reference Go implementation of Cadence, Flow's resource-oriented smart contract language (`module github.com/onflow/cadence`). The repo ships the lexer, parser, semantic checker, tree-walking interpre" in text, "expected to find: " + "Reference Go implementation of Cadence, Flow's resource-oriented smart contract language (`module github.com/onflow/cadence`). The repo ships the lexer, parser, semantic checker, tree-walking interpre"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Generated Go sources (105 files, counted via `grep -rl '// Code generated' . --include='*.go'`): `*_string.go` (stringer), `interpreter/subtype_check.gen.go`, `version.go`, and any file starting wit" in text, "expected to find: " + "- Generated Go sources (105 files, counted via `grep -rl '// Code generated' . --include='*.go'`): `*_string.go` (stringer), `interpreter/subtype_check.gen.go`, `version.go`, and any file starting wit"[:80]

