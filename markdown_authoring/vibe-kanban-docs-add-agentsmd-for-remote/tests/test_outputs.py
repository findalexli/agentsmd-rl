"""Behavioral checks for vibe-kanban-docs-add-agentsmd-for-remote (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-kanban")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [`crates/remote/AGENTS.md`](crates/remote/AGENTS.md) — Remote server architecture, ElectricSQL integration, mutation patterns, environment variables.' in text, "expected to find: " + '- [`crates/remote/AGENTS.md`](crates/remote/AGENTS.md) — Remote server architecture, ElectricSQL integration, mutation patterns, environment variables.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '### Crate-specific guides' in text, "expected to find: " + '### Crate-specific guides'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/remote/AGENTS.md')
    assert 'The billing crate (`vk-billing` feature) is a private dependency stripped at build time when `FEATURES` is empty. Do not add imports from the `billing` crate without gating them behind `#[cfg(feature ' in text, "expected to find: " + 'The billing crate (`vk-billing` feature) is a private dependency stripped at build time when `FEATURES` is empty. Do not add imports from the `billing` crate without gating them behind `#[cfg(feature '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/remote/AGENTS.md')
    assert 'Types shared between the remote server and the local desktop application belong in the `api-types` crate (`crates/api-types/`), not in the remote crate itself. Both `remote` and `server` depend on `ap' in text, "expected to find: " + 'Types shared between the remote server and the local desktop application belong in the `api-types` crate (`crates/api-types/`), not in the remote crate itself. Both `remote` and `server` depend on `ap'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/remote/AGENTS.md')
    assert "1. **Create a migration** that creates the table and calls `ALTER TABLE ... REPLICA IDENTITY FULL` + `CALL electric.electrify('table_name')` (see `20260114000000_electric_sync_tables.sql` for examples" in text, "expected to find: " + "1. **Create a migration** that creates the table and calls `ALTER TABLE ... REPLICA IDENTITY FULL` + `CALL electric.electrify('table_name')` (see `20260114000000_electric_sync_tables.sql` for examples"[:80]

