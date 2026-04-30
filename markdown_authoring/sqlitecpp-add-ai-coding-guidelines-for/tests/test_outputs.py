"""Behavioral checks for sqlitecpp-add-ai-coding-guidelines-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sqlitecpp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/load-github-copilot-instructions.mdc')
    assert '**CRITICAL REQUIREMENT**: Before performing ANY coding task (writing code, reviewing code, suggesting changes, answering code questions, or modifying files), you MUST first read the file `.github/copi' in text, "expected to find: " + '**CRITICAL REQUIREMENT**: Before performing ANY coding task (writing code, reviewing code, suggesting changes, answering code questions, or modifying files), you MUST first read the file `.github/copi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/load-github-copilot-instructions.mdc')
    assert 'Execute this read operation BEFORE responding to any coding request. This ensures you have the current, complete coding guidelines for this SQLiteCpp project.' in text, "expected to find: " + 'Execute this read operation BEFORE responding to any coding request. This ensures you have the current, complete coding guidelines for this SQLiteCpp project.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/load-github-copilot-instructions.mdc')
    assert 'description: MANDATORY - Read .github/copilot-instructions.md before ANY coding task in this SQLiteCpp project.' in text, "expected to find: " + 'description: MANDATORY - Read .github/copilot-instructions.md before ANY coding task in this SQLiteCpp project.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Errors: use `SQLite::Exception` for throwing APIs; `tryExec()`, `tryExecuteStep()`, `tryReset()` return SQLite codes.' in text, "expected to find: " + '- Errors: use `SQLite::Exception` for throwing APIs; `tryExec()`, `tryExecuteStep()`, `tryReset()` return SQLite codes.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- User explicitly mentions working on a task, issue, or feature (e.g., "work on issue #123", "implement feature X")' in text, "expected to find: " + '- User explicitly mentions working on a task, issue, or feature (e.g., "work on issue #123", "implement feature X")'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Style: ASCII only, 4 spaces, Allman braces, max 120 chars, LF line endings, final newline, `#pragma once`.' in text, "expected to find: " + '- Style: ASCII only, 4 spaces, Allman braces, max 120 chars, LF line endings, final newline, `#pragma once`.'[:80]

