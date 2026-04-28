"""Behavioral checks for nightwatch-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nightwatch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Match Laravel conventions**: When adding new fields to payloads, **always check Laravel's source code** for the property names. Convert camelCase property names to snake_case for JSON payloads. Us" in text, "expected to find: " + "- **Match Laravel conventions**: When adding new fields to payloads, **always check Laravel's source code** for the property names. Convert camelCase property names to snake_case for JSON payloads. Us"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Field naming - ALWAYS check Laravel source code**: **Before creating any new field names, check Laravel's source code for the property names.** Look at the actual class properties and methods in L" in text, "expected to find: " + "- **Field naming - ALWAYS check Laravel source code**: **Before creating any new field names, check Laravel's source code for the property names.** Look at the actual class properties and methods in L"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Complete records**: **All records must always contain all keys.** Optional fields should use appropriate sentinel values rather than being omitted from the record. This ensures consistent record s' in text, "expected to find: " + '- **Complete records**: **All records must always contain all keys.** Optional fields should use appropriate sentinel values rather than being omitted from the record. This ensures consistent record s'[:80]

