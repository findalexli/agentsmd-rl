"""Behavioral checks for phpstan-symfony-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-symfony")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**phpstan/phpstan-symfony** is a PHPStan extension that provides static analysis support for Symfony framework applications. It enhances PHPStan's understanding of Symfony-specific patterns by providi" in text, "expected to find: " + "**phpstan/phpstan-symfony** is a PHPStan extension that provides static analysis support for Symfony framework applications. It enhances PHPStan's understanding of Symfony-specific patterns by providi"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository supports **PHP 7.4+** (see `composer.json`: `"php": "^7.4 || ^8.0"`). All code must be compatible with PHP 7.4. Do not use language features introduced in PHP 8.0+ (named arguments, ma' in text, "expected to find: " + 'This repository supports **PHP 7.4+** (see `composer.json`: `"php": "^7.4 || ^8.0"`). All code must be compatible with PHP 7.4. Do not use language features introduced in PHP 8.0+ (named arguments, ma'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **`src/Type/Symfony/`** - Dynamic return type extensions (`DynamicMethodReturnTypeExtension`, `TypeSpecifyingExtension`) that teach PHPStan the return types of Symfony methods. Organized by feature ' in text, "expected to find: " + '- **`src/Type/Symfony/`** - Dynamic return type extensions (`DynamicMethodReturnTypeExtension`, `TypeSpecifyingExtension`) that teach PHPStan the return types of Symfony methods. Organized by feature '[:80]

