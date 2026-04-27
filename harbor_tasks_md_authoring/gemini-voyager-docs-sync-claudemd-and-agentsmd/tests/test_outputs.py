"""Behavioral checks for gemini-voyager-docs-sync-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gemini-voyager")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The bump script automatically updates `package.json`, `manifest.json`, and `manifest.dev.json`, then runs `bun run format`.' in text, "expected to find: " + 'The bump script automatically updates `package.json`, `manifest.json`, and `manifest.dev.json`, then runs `bun run format`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **Note**: This file is mirrored in `CLAUDE.md`. Keep both files in sync.' in text, "expected to find: " + '> **Note**: This file is mirrored in `CLAUDE.md`. Keep both files in sync.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'bun run bump              # Bumps patch version (e.g., 1.3.2 → 1.3.3)' in text, "expected to find: " + 'bun run bump              # Bumps patch version (e.g., 1.3.2 → 1.3.3)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> **Note**: This file is mirrored in `AGENTS.md`. Keep both files in sync.' in text, "expected to find: " + '> **Note**: This file is mirrored in `AGENTS.md`. Keep both files in sync.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'bun run test:watch          # Interactive watch mode' in text, "expected to find: " + 'bun run test:watch          # Interactive watch mode'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'bun run test:ui             # Visual UI test runner' in text, "expected to find: " + 'bun run test:ui             # Visual UI test runner'[:80]

