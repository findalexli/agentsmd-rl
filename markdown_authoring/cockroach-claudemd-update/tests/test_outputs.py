"""Behavioral checks for cockroach-claudemd-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cockroach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Block comments** (standalone line) use full sentences with capitalization and punctuation:' in text, "expected to find: " + '**Block comments** (standalone line) use full sentences with capitalization and punctuation:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CockroachDB consists of many components and subsystems. The file .github/CODEOWNERS is a' in text, "expected to find: " + 'CockroachDB consists of many components and subsystems. The file .github/CODEOWNERS is a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Inline comments** (end of code line) are lowercase without terminal punctuation:' in text, "expected to find: " + '**Inline comments** (end of code line) are lowercase without terminal punctuation:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/CLAUDE.md')
    assert '- **Underscore separation**: `start_key` not `startkey` (consistent with information_schema)' in text, "expected to find: " + '- **Underscore separation**: `start_key` not `startkey` (consistent with information_schema)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/CLAUDE.md')
    assert '- **Disambiguate primary key columns**: `zone_id`, `job_id`, `table_id` not just `id`' in text, "expected to find: " + '- **Disambiguate primary key columns**: `zone_id`, `job_id`, `table_id` not just `id`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/sql/CLAUDE.md')
    assert '- **Same concept = same word**: `variable`/`value` between different SHOW commands' in text, "expected to find: " + '- **Same concept = same word**: `variable`/`value` between different SHOW commands'[:80]

