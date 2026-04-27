"""Behavioral checks for ccusage-docspackages-add-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ccusage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/internal/AGENTS.md')
    assert 'packages/internal/AGENTS.md' in text, "expected to find: " + 'packages/internal/AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/terminal/AGENTS.md')
    assert 'packages/terminal/AGENTS.md' in text, "expected to find: " + 'packages/terminal/AGENTS.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/terminal/CLAUDE.md')
    assert 'This is a private internal package and should not be published to npm. It exists solely to provide terminal utilities for other packages in the monorepo.' in text, "expected to find: " + 'This is a private internal package and should not be published to npm. It exists solely to provide terminal utilities for other packages in the monorepo.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/terminal/CLAUDE.md')
    assert '- **In-Source Testing**: Tests are written in the same files using `if (import.meta.vitest != null)` blocks' in text, "expected to find: " + '- **In-Source Testing**: Tests are written in the same files using `if (import.meta.vitest != null)` blocks'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/terminal/CLAUDE.md')
    assert '- **CRITICAL**: NEVER use `await import()` dynamic imports anywhere, especially in test blocks' in text, "expected to find: " + '- **CRITICAL**: NEVER use `await import()` dynamic imports anywhere, especially in test blocks'[:80]

