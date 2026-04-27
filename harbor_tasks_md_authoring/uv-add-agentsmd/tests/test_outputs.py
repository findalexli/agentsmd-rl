"""Behavioral checks for uv-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uv")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- NEVER perform builds with the release profile, unless asked or reproducing performance issues' in text, "expected to find: " + '- NEVER perform builds with the release profile, unless asked or reproducing performance issues'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- NEVER update all dependencies in the lockfile and ALWAYS use `cargo update --precise` to make' in text, "expected to find: " + '- NEVER update all dependencies in the lockfile and ALWAYS use `cargo update --precise` to make'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- AVOID shortening variable names, e.g., use `version` instead of `ver`, and `requires_python`' in text, "expected to find: " + '- AVOID shortening variable names, e.g., use `version` instead of `ver`, and `requires_python`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

