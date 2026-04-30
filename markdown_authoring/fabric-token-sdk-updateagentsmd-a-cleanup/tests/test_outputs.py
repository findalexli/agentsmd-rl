"""Behavioral checks for fabric-token-sdk-updateagentsmd-a-cleanup (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fabric-token-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Focused Tests**: Modify `It(...)` to `FIt(...)` to focus, or `XIt(...)` to skip (never commit these changes)' in text, "expected to find: " + '- **Focused Tests**: Modify `It(...)` to `FIt(...)` to focus, or `XIt(...)` to skip (never commit these changes)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **Performance Tip**: Use `Ctrl+F` to jump to sections using anchor links (e.g., `#building-and-running`)' in text, "expected to find: " + '> **Performance Tip**: Use `Ctrl+F` to jump to sections using anchor links (e.g., `#building-and-running`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Chaincode packaging failed**: Verify `FAB_BINS` is set correctly and points to valid Fabric binaries' in text, "expected to find: " + '- **Chaincode packaging failed**: Verify `FAB_BINS` is set correctly and points to valid Fabric binaries'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

