"""Behavioral checks for oxcaml-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oxcaml")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'You are working on the OxCaml compiler, a performance-focused fork of OCaml with Jane Street extensions, including the Flambda 2 optimizer and CFG backend.' in text, "expected to find: " + 'You are working on the OxCaml compiler, a performance-focused fork of OCaml with Jane Street extensions, including the Flambda 2 optimizer and CFG backend.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If the execution of `autoconf` fails because the version is too old, try with `autoconf27` instead.' in text, "expected to find: " + 'If the execution of `autoconf` fails because the version is too old, try with `autoconf27` instead.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'make test-one TEST=test-dir/path.ml      # Run a single test testsuite/tests/test-dir/path.ml' in text, "expected to find: " + 'make test-one TEST=test-dir/path.ml      # Run a single test testsuite/tests/test-dir/path.ml'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

