"""Behavioral checks for hyperindex-chore-added-subgraph-migration-mdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert "12. **🚨 CRITICAL: Check entity type mismatches and database schema compatibility** - ALWAYS verify that the types you're setting in code match the schema entity property types exactly, and ensure data" in text, "expected to find: " + "12. **🚨 CRITICAL: Check entity type mismatches and database schema compatibility** - ALWAYS verify that the types you're setting in code match the schema entity property types exactly, and ensure data"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert '**IMPORTANT: After completing each step, ALWAYS run the Quality Check Checklist (see section 21) before proceeding to the next step. This prevents common issues from accumulating and makes debugging m' in text, "expected to find: " + '**IMPORTANT: After completing each step, ALWAYS run the Quality Check Checklist (see section 21) before proceeding to the next step. This prevents common issues from accumulating and makes debugging m'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert 'When migrating from TheGraph to Envio, contract state fetching patterns need to be updated. TheGraph uses `.bind()` patterns for contract state access, while Envio requires explicit RPC calls using th' in text, "expected to find: " + 'When migrating from TheGraph to Envio, contract state fetching patterns need to be updated. TheGraph uses `.bind()` patterns for contract state access, while Envio requires explicit RPC calls using th'[:80]

