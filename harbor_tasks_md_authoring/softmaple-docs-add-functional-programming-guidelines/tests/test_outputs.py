"""Behavioral checks for softmaple-docs-add-functional-programming-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/softmaple")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'This file contains specific instructions for Claude AI when working on the Softmaple codebase.' in text, "expected to find: " + 'This file contains specific instructions for Claude AI when working on the Softmaple codebase.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '2. If on `next`, create a new feature branch: `git checkout -b type/description-$(date +%s)`' in text, "expected to find: " + '2. If on `next`, create a new feature branch: `git checkout -b type/description-$(date +%s)`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'const updateMap = <K, V>(map: ReadonlyMap<K, V>, key: K, value: V): Map<K, V> =>' in text, "expected to find: " + 'const updateMap = <K, V>(map: ReadonlyMap<K, V>, key: K, value: V): Map<K, V> =>'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **IMPORTANT: Never commit directly to the `next` branch.** Always create a new feature branch before making changes if you are on the default `next` branch.' in text, "expected to find: " + '- **IMPORTANT: Never commit directly to the `next` branch.** Always create a new feature branch before making changes if you are on the default `next` branch.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Immutability:** Avoid mutating data structures; return new copies instead (use spread operators, `Array.map()`, `Object.freeze()`, etc.)' in text, "expected to find: " + '- **Immutability:** Avoid mutating data structures; return new copies instead (use spread operators, `Array.map()`, `Object.freeze()`, etc.)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Higher-order functions:** Leverage functions that take or return other functions (e.g., `map`, `filter`, `reduce`)' in text, "expected to find: " + '- **Higher-order functions:** Leverage functions that take or return other functions (e.g., `map`, `filter`, `reduce`)'[:80]

