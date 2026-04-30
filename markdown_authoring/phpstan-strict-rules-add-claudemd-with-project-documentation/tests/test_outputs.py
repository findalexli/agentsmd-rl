"""Behavioral checks for phpstan-strict-rules-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-strict-rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**phpstan/phpstan-strict-rules** is a PHPStan extension that provides extra strict and opinionated rules for PHP static analysis. While PHPStan focuses on finding bugs, this package enforces strictly ' in text, "expected to find: " + '**phpstan/phpstan-strict-rules** is a PHPStan extension that provides extra strict and opinionated rules for PHP static analysis. While PHPStan focuses on finding bugs, this package enforces strictly '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Do not use PHP 8.0+ syntax** (named arguments, match expressions, union type hints in signatures, etc.) in the source code. Property declarations with types (e.g., `private Type $prop;`) are allowed' in text, "expected to find: " + '**Do not use PHP 8.0+ syntax** (named arguments, match expressions, union type hints in signatures, etc.) in the source code. Property declarations with types (e.g., `private Type $prop;`) are allowed'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Sets stricter PHPStan defaults** (lines 1-16): Parameters like `checkDynamicProperties`, `reportMaybesInMethodSignatures`, `checkFunctionNameCase`, etc. These are always active when the extension' in text, "expected to find: " + '1. **Sets stricter PHPStan defaults** (lines 1-16): Parameters like `checkDynamicProperties`, `reportMaybesInMethodSignatures`, `checkFunctionNameCase`, etc. These are always active when the extension'[:80]

