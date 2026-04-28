"""Behavioral checks for phpstan-webmozart-assert-add-claudemd-with-project-documenta (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-webmozart-assert")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'PHPStan cannot natively understand type narrowing from `Webmozart\\Assert\\Assert` static method calls. This extension teaches PHPStan to refine types after assertions like `Assert::integer($a)`, `Asser' in text, "expected to find: " + 'PHPStan cannot natively understand type narrowing from `Webmozart\\Assert\\Assert` static method calls. This extension teaches PHPStan to refine types after assertions like `Assert::integer($a)`, `Asser'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "For each supported `Assert::*` method, the extension translates the assertion into an equivalent PHP expression (using php-parser AST nodes) that PHPStan's type specifier already understands. For exam" in text, "expected to find: " + "For each supported `Assert::*` method, the extension translates the assertion into an equivalent PHP expression (using php-parser AST nodes) that PHPStan's type specifier already understands. For exam"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The extension registers `AssertTypeSpecifyingExtension` as a `phpstan.typeSpecifier.staticMethodTypeSpecifyingExtension` in `extension.neon`. This class implements `StaticMethodTypeSpecifyingExtension' in text, "expected to find: " + 'The extension registers `AssertTypeSpecifyingExtension` as a `phpstan.typeSpecifier.staticMethodTypeSpecifyingExtension` in `extension.neon`. This class implements `StaticMethodTypeSpecifyingExtension'[:80]

