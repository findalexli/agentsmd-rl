"""Behavioral checks for kotlin-sdk-docs-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kotlin-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Write comprehensive tests for new features. Always add tests for new features or bug fixes, even if not explicitly requested.' in text, "expected to find: " + '- Write comprehensive tests for new features. Always add tests for new features or bug fixes, even if not explicitly requested.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `val` for immutable properties and `var` for mutable; consider `lateinit var` instead of nullable types when appropriate' in text, "expected to find: " + '- Use `val` for immutable properties and `var` for mutable; consider `lateinit var` instead of nullable types when appropriate'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '10. **Prefer using MCP servers** like `jetbrains` and `intellij-index` for code navigation, analysis, and refactoring.' in text, "expected to find: " + '10. **Prefer using MCP servers** like `jetbrains` and `intellij-index` for code navigation, analysis, and refactoring.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

