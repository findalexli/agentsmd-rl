"""Behavioral checks for phpstan-mockery-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-mockery")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This extension teaches PHPStan to understand Mockery's dynamic mock creation patterns so that static analysis works correctly with mocked objects. Without this extension, PHPStan cannot infer the corr" in text, "expected to find: " + "This extension teaches PHPStan to understand Mockery's dynamic mock creation patterns so that static analysis works correctly with mocked objects. Without this extension, PHPStan cannot infer the corr"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository supports **PHP 7.4+**. The `composer.json` platform is set to PHP 7.4.6. Do not use language features unavailable in PHP 7.4 (e.g. enums, fibers, readonly properties, intersection type' in text, "expected to find: " + 'This repository supports **PHP 7.4+**. The `composer.json` platform is set to PHP 7.4.6. Do not use language features unavailable in PHP 7.4 (e.g. enums, fibers, readonly properties, intersection type'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Tests are integration tests that create actual Mockery mocks and verify PHPStan correctly understands the types. Some tests extend `PHPUnit\\Framework\\TestCase`, others extend `Mockery\\Adapter\\Phpunit\\' in text, "expected to find: " + 'Tests are integration tests that create actual Mockery mocks and verify PHPStan correctly understands the types. Some tests extend `PHPUnit\\Framework\\TestCase`, others extend `Mockery\\Adapter\\Phpunit\\'[:80]

