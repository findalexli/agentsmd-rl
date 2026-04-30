"""Behavioral checks for phpstan-nette-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-nette")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**phpstan/phpstan-nette** is a PHPStan extension that provides static analysis support for the [Nette Framework](https://nette.org/). It teaches PHPStan to understand Nette-specific patterns such as d' in text, "expected to find: " + '**phpstan/phpstan-nette** is a PHPStan extension that provides static analysis support for the [Nette Framework](https://nette.org/). It teaches PHPStan to understand Nette-specific patterns such as d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Dynamic Return Type Extensions** (`src/Type/Nette/`): Teach PHPStan the return types of Nette methods that depend on arguments or context (e.g., `Container::getComponent()` return type based on `' in text, "expected to find: " + '1. **Dynamic Return Type Extensions** (`src/Type/Nette/`): Teach PHPStan the return types of Nette methods that depend on arguments or context (e.g., `Container::getComponent()` return type based on `'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository supports **PHP 7.4+** (not just PHP 8.1+ like phpstan-src). All code must be compatible with PHP 7.4, 8.0, 8.1, 8.2, 8.3, and 8.4. Do not use language features unavailable in PHP 7.4.' in text, "expected to find: " + 'This repository supports **PHP 7.4+** (not just PHP 8.1+ like phpstan-src). All code must be compatible with PHP 7.4, 8.0, 8.1, 8.2, 8.3, and 8.4. Do not use language features unavailable in PHP 7.4.'[:80]

