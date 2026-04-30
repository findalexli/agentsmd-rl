"""Behavioral checks for extension-installer-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/extension-installer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**phpstan/extension-installer** is a Composer plugin that automatically registers PHPStan extensions. Without it, users must manually add `includes` entries in their `phpstan.neon` for every installed' in text, "expected to find: " + '**phpstan/extension-installer** is a Composer plugin that automatically registers PHPStan extensions. Without it, users must manually add `includes` entries in their `phpstan.neon` for every installed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This project uses [phpstan/build-cs](https://github.com/phpstan/build-cs) (branch `2.x`) for coding standards via PHP_CodeSniffer. The `phpcs.xml` configures `php_version` as `70400` (PHP 7.4). To set' in text, "expected to find: " + 'This project uses [phpstan/build-cs](https://github.com/phpstan/build-cs) (branch `2.x`) for coding standards via PHP_CodeSniffer. The `phpcs.xml` configures `php_version` as `70400` (PHP 7.4). To set'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Integration test**: Installs `phpstan-phpunit` via the extension installer, runs PHPStan analysis on a test file, then verifies it works after renaming the directory (testing relative path handlin' in text, "expected to find: " + '- **Integration test**: Installs `phpstan-phpunit` via the extension installer, runs PHPStan analysis on a test file, then verifies it works after renaming the directory (testing relative path handlin'[:80]

