"""Behavioral checks for eslint-interactive-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eslint-interactive")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`eslint-interactive` is an interactive CLI tool that groups ESLint problems by rule and allows users to apply per-rule fixes (auto-fix, disable comments, convert to warnings, etc.). It solves the prob' in text, "expected to find: " + '`eslint-interactive` is an interactive CLI tool that groups ESLint problems by rule and allows users to apply per-rule fixes (auto-fix, disable comments, convert to warnings, etc.). It solves the prob'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Methods: `lint()`, `formatResultSummary()`, `formatResultDetails()`, `applyAutoFixes()`, `disablePerLine()`, `disablePerFile()`, `convertErrorToWarningPerFile()`, `applySuggestions()`, `makeFixableA' in text, "expected to find: " + '- Methods: `lint()`, `formatResultSummary()`, `formatResultDetails()`, `applyAutoFixes()`, `disablePerLine()`, `disablePerFile()`, `convertErrorToWarningPerFile()`, `applySuggestions()`, `makeFixableA'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Low-level fix implementations, one file per action type. Each takes ESLint lint results and returns text edits. Uses ESLint's `Rule.RuleFixer` API internally." in text, "expected to find: " + "Low-level fix implementations, one file per action type. Each takes ESLint lint results and returns text edits. Uses ESLint's `Rule.RuleFixer` API internally."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

