"""Behavioral checks for rigraph-docs-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rigraph")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '> **Note**: For general development guidelines, code style conventions, and AI agent instructions, see [`AGENTS.md`](../AGENTS.md) in the repository root.' in text, "expected to find: " + '> **Note**: For general development guidelines, code style conventions, and AI agent instructions, see [`AGENTS.md`](../AGENTS.md) in the repository root.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Run tests: `testthat::test_local(reporter = "check")`' in text, "expected to find: " + '- Run tests: `testthat::test_local(reporter = "check")`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '# GitHub Copilot Instructions for igraph/rigraph' in text, "expected to find: " + '# GitHub Copilot Instructions for igraph/rigraph'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'It provides routines for simple graphs and network analysis, handles large graphs efficiently, and includes functions for generating random and regular graphs, graph visualization, centrality methods,' in text, "expected to find: " + 'It provides routines for simple graphs and network analysis, handles large graphs efficiently, and includes functions for generating random and regular graphs, graph visualization, centrality methods,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- IMPORTANT: PR titles end up in `NEWS.md` grouped by conventional commit label. PRs and commits use the conventional commit style with backticks for code references such as `function_call()`' in text, "expected to find: " + '- IMPORTANT: PR titles end up in `NEWS.md` grouped by conventional commit label. PRs and commits use the conventional commit style with backticks for code references such as `function_call()`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `max` for maximal (graph theory term: a vertex is maximal if no other vertex dominates it) and `largest` for maximum (the biggest value in a set)' in text, "expected to find: " + '- Use `max` for maximal (graph theory term: a vertex is maximal if no other vertex dominates it) and `largest` for maximum (the biggest value in a set)'[:80]

