"""Behavioral checks for sqlserver.rules-add-comprehensive-github-copilot-instruction (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sqlserver.rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'SqlServer.Rules is a .NET library and command line tool that provides static code analysis for SQL Server projects, implementing more than 140 rules for design, naming, and performance analysis. The s' in text, "expected to find: " + 'SqlServer.Rules is a .NET library and command line tool that provides static code analysis for SQL Server projects, implementing more than 140 rules for design, naming, and performance analysis. The s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Remember: This codebase analyzes SQL code quality using Microsoft DacFx. Always test rule changes against real SQL scenarios and ensure new rules follow existing patterns for consistency.' in text, "expected to find: " + 'Remember: This codebase analyzes SQL code quality using Microsoft DacFx. Always test rule changes against real SQL scenarios and ensure new rules follow existing patterns for consistency.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]

