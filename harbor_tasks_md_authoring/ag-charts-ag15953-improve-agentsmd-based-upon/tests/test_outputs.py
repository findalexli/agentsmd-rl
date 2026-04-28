"""Behavioral checks for ag-charts-ag15953-improve-agentsmd-based-upon (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ag-charts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '-   **Test real implementations, not helpers**: Avoid creating test helper functions that duplicate production logic. Instead, test the actual implementation through its public API (e.g., using `DataS' in text, "expected to find: " + '-   **Test real implementations, not helpers**: Avoid creating test helper functions that duplicate production logic. Instead, test the actual implementation through its public API (e.g., using `DataS'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '-   **Test verification patterns:** When writing or modifying tests, review similar tests to ensure consistent verification patterns (e.g., if similar tests verify domains, your tests should too).' in text, "expected to find: " + '-   **Test verification patterns:** When writing or modifying tests, review similar tests to ensure consistent verification patterns (e.g., if similar tests verify domains, your tests should too).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '-   **Naming clarity**: Variable and parameter names should clearly convey intent, especially for boolean flags (e.g., `columnNeedValueOf` is clearer than `columnValueTypes` for a boolean array).' in text, "expected to find: " + '-   **Naming clarity**: Variable and parameter names should clearly convey intent, especially for boolean flags (e.g., `columnNeedValueOf` is clearer than `columnValueTypes` for a boolean array).'[:80]

