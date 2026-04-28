"""Behavioral checks for flowglad-add-ast-grep-to-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flowglad")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.' in text, "expected to find: " + 'ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'Remember that you have `ast-grep` CLI at your disposal.' in text, "expected to find: " + 'Remember that you have `ast-grep` CLI at your disposal.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert '## Resources' in text, "expected to find: " + '## Resources'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('platform/flowglad-next/claude.md')
    assert 'ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.' in text, "expected to find: " + 'ast-grep is a code tool for structural search and replace. It is like syntax-aware grep/sed! You can write code patterns to locate and modify code, based on AST, in thousands of files, interactively.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('platform/flowglad-next/claude.md')
    assert 'Remember that you have `ast-grep` CLI at your disposal.' in text, "expected to find: " + 'Remember that you have `ast-grep` CLI at your disposal.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('platform/flowglad-next/claude.md')
    assert '### ast-grep' in text, "expected to find: " + '### ast-grep'[:80]

