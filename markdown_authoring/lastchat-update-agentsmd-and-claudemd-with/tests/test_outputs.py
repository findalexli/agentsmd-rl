"""Behavioral checks for lastchat-update-agentsmd-and-claudemd-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lastchat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   **Lists:** Never pass mutable collections (`SnapshotStateList`) directly to `LazyColumn` items. Use `derivedStateOf` to pass simple, immutable states (e.g., `Boolean`) to prevent unnecessary recom' in text, "expected to find: " + '-   **Lists:** Never pass mutable collections (`SnapshotStateList`) directly to `LazyColumn` items. Use `derivedStateOf` to pass simple, immutable states (e.g., `Boolean`) to prevent unnecessary recom'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   When updating `StateFlow` in services (e.g., `ChatService`), **snapshot** the current value into a local variable before applying complex transformations to avoid race conditions.' in text, "expected to find: " + '-   When updating `StateFlow` in services (e.g., `ChatService`), **snapshot** the current value into a local variable before applying complex transformations to avoid race conditions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   **Motion:** **Strictly NO Linear (Tween) animations.** All motion must use physics-based interpolators (springs) to convey momentum and weight.' in text, "expected to find: " + '-   **Motion:** **Strictly NO Linear (Tween) animations.** All motion must use physics-based interpolators (springs) to convey momentum and weight.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

