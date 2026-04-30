"""Behavioral checks for mono-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mono")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Zero follows a **sync-first** model: client queries are reactive and automatically update when server data changes. ZQL queries are transformed to SQL on the server and results are incrementally maint' in text, "expected to find: " + 'Zero follows a **sync-first** model: client queries are reactive and automatically update when server data changes. ZQL queries are transformed to SQL on the server and results are incrementally maint'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This monorepo contains **Zero** (real-time sync platform) and **Replicache** (client-side data layer), built as complementary technologies for building reactive, sync-enabled applications.' in text, "expected to find: " + 'This monorepo contains **Zero** (real-time sync platform) and **Replicache** (client-side data layer), built as complementary technologies for building reactive, sync-enabled applications.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Multiple vitest configs for different environments (e.g., `vitest.config.pg-16.ts` for PostgreSQL tests)' in text, "expected to find: " + '- Multiple vitest configs for different environments (e.g., `vitest.config.pg-16.ts` for PostgreSQL tests)'[:80]

