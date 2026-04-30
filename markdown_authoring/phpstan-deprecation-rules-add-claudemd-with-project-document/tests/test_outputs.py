"""Behavioral checks for phpstan-deprecation-rules-add-claudemd-with-project-document (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-deprecation-rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Usage of deprecated code inside code that is itself deprecated is not reported. This is handled by the `DeprecatedScopeHelper` which aggregates `DeprecatedScopeResolver` implementations. The `DefaultD' in text, "expected to find: " + 'Usage of deprecated code inside code that is itself deprecated is not reported. This is handled by the `DeprecatedScopeHelper` which aggregates `DeprecatedScopeResolver` implementations. The `DefaultD'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Restricted usage extensions** (implementing PHPStan's `Restricted*UsageExtension` interfaces) handle most deprecation checks: class names, methods, functions, properties, and class constants. Thes" in text, "expected to find: " + "- **Restricted usage extensions** (implementing PHPStan's `Restricted*UsageExtension` interfaces) handle most deprecation checks: class names, methods, functions, properties, and class constants. Thes"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**phpstan/phpstan-deprecation-rules** is a PHPStan extension that detects usage of deprecated code. It reports errors when your code uses classes, methods, functions, properties, constants, traits, or' in text, "expected to find: " + '**phpstan/phpstan-deprecation-rules** is a PHPStan extension that detects usage of deprecated code. It reports errors when your code uses classes, methods, functions, properties, constants, traits, or'[:80]

