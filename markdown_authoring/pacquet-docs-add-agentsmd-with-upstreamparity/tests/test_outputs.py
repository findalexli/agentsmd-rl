"""Behavioral checks for pacquet-docs-add-agentsmd-with-upstreamparity (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pacquet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/naming.html)' in text, "expected to find: " + '- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/naming.html)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Never ignore a test failure.** Do not dismiss a failing test as "pre-existing"' in text, "expected to find: " + '**Never ignore a test failure.** Do not dismiss a failing test as "pre-existing"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'its behavior, flags, defaults, error codes, file formats, and directory layout' in text, "expected to find: " + 'its behavior, flags, defaults, error codes, file formats, and directory layout'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

