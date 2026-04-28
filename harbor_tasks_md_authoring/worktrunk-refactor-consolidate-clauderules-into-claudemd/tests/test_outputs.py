"""Behavioral checks for worktrunk-refactor-consolidate-clauderules-into-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/worktrunk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/accessor-conventions.md')
    assert '.claude/rules/accessor-conventions.md' in text, "expected to find: " + '.claude/rules/accessor-conventions.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/caching-strategy.md')
    assert '.claude/rules/caching-strategy.md' in text, "expected to find: " + '.claude/rules/caching-strategy.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/output-system-architecture.md')
    assert '.claude/rules/output-system-architecture.md' in text, "expected to find: " + '.claude/rules/output-system-architecture.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-user-outputs/SKILL.md')
    assert 'description: CLI output formatting standards for worktrunk. Use when writing user-facing messages, error handling, progress output, hints, warnings, or working with the output system.' in text, "expected to find: " + 'description: CLI output formatting standards for worktrunk. Use when writing user-facing messages, error handling, progress output, hints, warnings, or working with the output system.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-user-outputs/SKILL.md')
    assert '**Decision principle:** If this command is piped, what should the receiving program get?' in text, "expected to find: " + '**Decision principle:** If this command is piped, what should the receiving program get?'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-user-outputs/SKILL.md')
    assert '| `is_shell_integration_active()` | — | Check if directive file set (rarely needed) |' in text, "expected to find: " + '| `is_shell_integration_active()` | — | Check if directive file set (rarely needed) |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`Repository` holds its cache directly via `Arc<RepoCache>`. Cloning a Repository shares the cache — all clones see the same cached values.' in text, "expected to find: " + '`Repository` holds its cache directly via `Arc<RepoCache>`. Cloning a Repository shares the cache — all clones see the same cached values.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| (bare noun) | `Option<T>` or `T` | None (may cache) | Returns None/default if absent | `config()`, `switch_previous()` |' in text, "expected to find: " + '| (bare noun) | `Option<T>` or `T` | None (may cache) | Returns None/default if absent | `config()`, `switch_previous()` |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `set_*` | `Result<()>` | Writes state | Errors on failure | `set_switch_previous()`, `set_config()` |' in text, "expected to find: " + '| `set_*` | `Result<()>` | Writes state | Errors on failure | `set_switch_previous()`, `set_config()` |'[:80]

