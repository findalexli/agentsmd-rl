"""Behavioral checks for phpstan-disallowed-calls-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan-disallowed-calls")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Rule-analysis tests extend `RuleTestCase`. The rule configuration is passed inline in `getRule()`, not via neon files. `$this->analyse()` takes a fixture file and an array of expected errors as `[mess' in text, "expected to find: " + 'Rule-analysis tests extend `RuleTestCase`. The rule configuration is passed inline in `getRule()`, not via neon files. `$this->analyse()` takes a fixture file and an array of expected errors as `[mess'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`extension.neon` is the entry point wiring all rules together. Each feature has its own documentation file in `docs/` — new features get their own doc or extend an existing one.' in text, "expected to find: " + '`extension.neon` is the entry point wiring all rules together. Each feature has its own documentation file in `docs/` — new features get their own doc or extend an existing one.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Test classes live in `tests/Calls/`, `tests/Usages/`, `tests/ControlStructures/` etc. Fixture files (PHP files analysed by the tests) live in `tests/src/`.' in text, "expected to find: " + 'Test classes live in `tests/Calls/`, `tests/Usages/`, `tests/ControlStructures/` etc. Fixture files (PHP files analysed by the tests) live in `tests/src/`.'[:80]

