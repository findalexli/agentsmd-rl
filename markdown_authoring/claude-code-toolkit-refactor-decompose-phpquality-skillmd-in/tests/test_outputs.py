"""Behavioral checks for claude-code-toolkit-refactor-decompose-phpquality-skillmd-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/SKILL.md')
    assert '| union types, intersection types, DNF, enums, readonly, named arguments, match expression, null-safe operator, PHP 8.0, PHP 8.1, PHP 8.2 | `references/modern-php-features.md` | ~160 lines |' in text, "expected to find: " + '| union types, intersection types, DNF, enums, readonly, named arguments, match expression, null-safe operator, PHP 8.0, PHP 8.1, PHP 8.2 | `references/modern-php-features.md` | ~160 lines |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/SKILL.md')
    assert "**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references." in text, "expected to find: " + "**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/SKILL.md')
    assert 'Every PHP file must begin with `declare(strict_types=1)`. This enforces scalar type coercion rules, catching type errors at call time instead of silently converting values.' in text, "expected to find: " + 'Every PHP file must begin with `declare(strict_types=1)`. This enforces scalar type coercion rules, catching type errors at call time instead of silently converting values.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/framework-idioms.md')
    assert '> **Scope**: Idiomatic patterns for Laravel and Symfony. Covers Eloquent scopes, Collections, Service Container binding, Symfony DI attributes, and Event Dispatcher. Does NOT cover raw PHP patterns wi' in text, "expected to find: " + '> **Scope**: Idiomatic patterns for Laravel and Symfony. Covers Eloquent scopes, Collections, Service Container binding, Symfony DI attributes, and Event Dispatcher. Does NOT cover raw PHP patterns wi'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/framework-idioms.md')
    assert 'use Symfony\\Component\\EventDispatcher\\Attribute\\AsEventListener;' in text, "expected to find: " + 'use Symfony\\Component\\EventDispatcher\\Attribute\\AsEventListener;'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/framework-idioms.md')
    assert '$this->app->bind(PaymentGateway::class, StripeGateway::class);' in text, "expected to find: " + '$this->app->bind(PaymentGateway::class, StripeGateway::class);'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/modern-php-features.md')
    assert '> **Scope**: PHP 8.0, 8.1, and 8.2 language features relevant to code quality reviews: type system improvements, enums, readonly, match expressions, named arguments, null-safe operator. Does NOT cover' in text, "expected to find: " + '> **Scope**: PHP 8.0, 8.1, and 8.2 language features relevant to code quality reviews: type system improvements, enums, readonly, match expressions, named arguments, null-safe operator. Does NOT cover'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/modern-php-features.md')
    assert '`match` is a stricter alternative to `switch`. It uses strict comparison (`===`), returns a value, and throws `UnhandledMatchError` for missing cases.' in text, "expected to find: " + '`match` is a stricter alternative to `switch`. It uses strict comparison (`===`), returns a value, and throws `UnhandledMatchError` for missing cases.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/modern-php-features.md')
    assert 'The `?->` operator short-circuits to `null` when the left side is null, eliminating nested null checks.' in text, "expected to find: " + 'The `?->` operator short-circuits to `null` when the left side is null, eliminating nested null checks.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/quality-tools.md')
    assert 'Alternative to PHPStan with taint analysis for security-sensitive code paths. Shows data flow from user input to dangerous sinks (SQL queries, shell commands, file operations). Use `--show-info=true` ' in text, "expected to find: " + 'Alternative to PHPStan with taint analysis for security-sensitive code paths. Shows data flow from user input to dangerous sinks (SQL queries, shell commands, file operations). Use `--show-info=true` '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/quality-tools.md')
    assert 'Static analysis with levels 0 through 9. Level 6 is the recommended minimum for production code: it covers method return types, property types, and dead code detection. Higher levels add strictness ar' in text, "expected to find: " + 'Static analysis with levels 0 through 9. Level 6 is the recommended minimum for production code: it covers method return types, property types, and dead code detection. Higher levels add strictness ar'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-quality/references/quality-tools.md')
    assert '> **Scope**: PHP code quality tool configuration and usage: PHP-CS-Fixer, PHPStan, Psalm, Rector. Covers CI integration commands, config files, and recommended strictness levels. Does NOT cover langua' in text, "expected to find: " + '> **Scope**: PHP code quality tool configuration and usage: PHP-CS-Fixer, PHPStan, Psalm, Rector. Covers CI integration commands, config files, and recommended strictness levels. Does NOT cover langua'[:80]

