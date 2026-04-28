"""Behavioral checks for core-docs-update-cursor-cloud-supabase (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "7. **Note**: Migration `20260226113000_authz_memberships_foundation.sql` has an index expression (`COALESCE(staff_role::text, '')`) that Postgres rejects as non-IMMUTABLE. Create the `authz` schema, t" in text, "expected to find: " + "7. **Note**: Migration `20260226113000_authz_memberships_foundation.sql` has an index expression (`COALESCE(staff_role::text, '')`) that Postgres rejects as non-IMMUTABLE. Create the `authz` schema, t"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Known issue**: Migration `20260214090000_foundation_1_schema.sql` uses `LOCK TABLE` outside a transaction block, which fails with the Supabase CLI. Later migrations also have dependency chains that ' in text, "expected to find: " + '**Known issue**: Migration `20260214090000_foundation_1_schema.sql` uses `LOCK TABLE` outside a transaction block, which fails with the Supabase CLI. Later migrations also have dependency chains that '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. Move **all** `2026*` migrations and `seed.sql` out: `mkdir -p /tmp/supabase_mig_staging && for f in supabase/migrations/2026*.sql; do mv "$f" /tmp/supabase_mig_staging/; done && mv supabase/seed.sq' in text, "expected to find: " + '1. Move **all** `2026*` migrations and `seed.sql` out: `mkdir -p /tmp/supabase_mig_staging && for f in supabase/migrations/2026*.sql; do mv "$f" /tmp/supabase_mig_staging/; done && mv supabase/seed.sq'[:80]

