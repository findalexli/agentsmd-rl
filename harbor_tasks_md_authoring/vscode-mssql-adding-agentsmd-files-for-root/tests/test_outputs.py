"""Behavioral checks for vscode-mssql-adding-agentsmd-files-for-root (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-mssql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The MSSQL Extension for Visual Studio Code is a TypeScript-based VS Code extension that provides database management capabilities for SQL Server, Azure SQL, and SQL Database in Fabric. The extension i' in text, "expected to find: " + 'The MSSQL Extension for Visual Studio Code is a TypeScript-based VS Code extension that provides database management capabilities for SQL Server, Azure SQL, and SQL Database in Fabric. The extension i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Always reference these instructions first** and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + '**Always reference these instructions first** and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**NEVER CANCEL** any build or test commands. These operations can take significant time and should be allowed to complete.' in text, "expected to find: " + '**NEVER CANCEL** any build or test commands. These operations can take significant time and should be allowed to complete.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('test/unit/AGENTS.md')
    assert '* Do not edit application/source files unless the refactor demands it.  Confirm before editing files outside of /test/unit, and justify why you need to make those changes.' in text, "expected to find: " + '* Do not edit application/source files unless the refactor demands it.  Confirm before editing files outside of /test/unit, and justify why you need to make those changes.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('test/unit/AGENTS.md')
    assert "* Avoid Object.defineProperty hacks and (if possible) fake/partial plain objects; use sandbox.createStubInstance(type) and sandbox.stub(obj, 'prop').value(...)." in text, "expected to find: " + "* Avoid Object.defineProperty hacks and (if possible) fake/partial plain objects; use sandbox.createStubInstance(type) and sandbox.stub(obj, 'prop').value(...)."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('test/unit/AGENTS.md')
    assert "* Orgnize the contents of each commit with test files that make sense together.  It's okay for each .test.ts file to have its own commit if they're not related." in text, "expected to find: " + "* Orgnize the contents of each commit with test files that make sense together.  It's okay for each .test.ts file to have its own commit if they're not related."[:80]

