"""Behavioral checks for openfga-docs-add-agentmd-with-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openfga")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Graph/ListObjects changes**: When modifying `internal/graph/` or `server/commands/reverseexpand/`, review and stress test matrix tests in `tests/check/` and `tests/listobjects/` to ensure edge cas' in text, "expected to find: " + '- **Graph/ListObjects changes**: When modifying `internal/graph/` or `server/commands/reverseexpand/`, review and stress test matrix tests in `tests/check/` and `tests/listobjects/` to ensure edge cas'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'OpenFGA is a high-performance authorization engine inspired by Google Zanzibar. It evaluates relationship-based access control queries.' in text, "expected to find: " + 'OpenFGA is a high-performance authorization engine inspired by Google Zanzibar. It evaluates relationship-based access control queries.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `storage.go` - Core interfaces (RelationshipTupleReader, RelationshipTupleWriter, OpenFGADatastore)' in text, "expected to find: " + '- `storage.go` - Core interfaces (RelationshipTupleReader, RelationshipTupleWriter, OpenFGADatastore)'[:80]

