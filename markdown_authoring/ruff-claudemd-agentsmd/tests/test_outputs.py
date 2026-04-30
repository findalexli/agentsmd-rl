"""Behavioral checks for ruff-claudemd-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruff")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- When adding new ty checks, it's important to make error messages concise. Think about how an error message would look on a narrow terminal screen. Sometimes more detail can be provided in subdiagnos" in text, "expected to find: " + "- When adding new ty checks, it's important to make error messages concise. Think about how an error message would look on a narrow terminal screen. Sometimes more detail can be provided in subdiagnos"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains both Ruff (a Python linter and formatter) and ty (a Python type checker). The crates follow a naming convention: `ruff_*` for Ruff-specific code and `ty_*` for ty-specific cod' in text, "expected to find: " + 'This repository contains both Ruff (a Python linter and formatter) and ty (a Python type checker). The crates follow a naming convention: `ruff_*` for Ruff-specific code and `ty_*` for ty-specific cod'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Try hard to avoid patterns that require `panic!`, `unreachable!`, or `.unwrap()`. Instead, try to encode those constraints in the type system. Don't be afraid to write code that's more verbose or re" in text, "expected to find: " + "- Try hard to avoid patterns that require `panic!`, `unreachable!`, or `.unwrap()`. Instead, try to encode those constraints in the type system. Don't be afraid to write code that's more verbose or re"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

