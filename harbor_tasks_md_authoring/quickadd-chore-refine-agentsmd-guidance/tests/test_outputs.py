"""Behavioral checks for quickadd-chore-refine-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quickadd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'QuickAdd is an Obsidian community plugin that provides four choice types:' in text, "expected to find: " + 'QuickAdd is an Obsidian community plugin that provides four choice types:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `bun` for package management and scripts. Avoid npm/yarn/pnpm.' in text, "expected to find: " + '- Use `bun` for package management and scripts. Avoid npm/yarn/pnpm.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use the GitHub CLI (`gh`) for issues, PRs, and releases.' in text, "expected to find: " + '- Use the GitHub CLI (`gh`) for issues, PRs, and releases.'[:80]

