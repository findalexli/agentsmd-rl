"""Behavioral checks for pgledger-add-an-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pgledger")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Tests are Go integration tests in `go/test/` using pgx and testify. They connect to PostgreSQL at `postgres://pgledger:pgledger@localhost:5432/pgledger`. All tests call the SQL functions directly and ' in text, "expected to find: " + 'Tests are Go integration tests in `go/test/` using pgx and testify. They connect to PostgreSQL at `postgres://pgledger:pgledger@localhost:5432/pgledger`. All tests call the SQL functions directly and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Test helpers in `go/test/test_helpers.go` define Go structs (Account, Transfer, Entry) that map to the view columns, plus helper functions for creating accounts, transfers, and querying entries.' in text, "expected to find: " + 'Test helpers in `go/test/test_helpers.go` define Go structs (Account, Transfer, Entry) that map to the view columns, plus helper functions for creating accounts, transfers, and querying entries.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Views (`pgledger_accounts_view`, `pgledger_transfers_view`, `pgledger_entries_view`) are the public query interface. The entries view joins to transfers to include `event_at` and `metadata`.' in text, "expected to find: " + 'Views (`pgledger_accounts_view`, `pgledger_transfers_view`, `pgledger_entries_view`) are the public query interface. The entries view joins to transfers to include `event_at` and `metadata`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

