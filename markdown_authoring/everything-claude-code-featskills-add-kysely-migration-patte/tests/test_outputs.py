"""Behavioral checks for everything-claude-code-featskills-add-kysely-migration-patte (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-migrations/SKILL.md')
    assert 'description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Kysely, Django,' in text, "expected to find: " + 'description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Kysely, Django,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-migrations/SKILL.md')
    assert '// Migrations are frozen in time and must not depend on current schema types.' in text, "expected to find: " + '// Migrations are frozen in time and must not depend on current schema types.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/database-migrations/SKILL.md')
    assert ".addColumn('email', 'varchar(255)', (col) => col.notNull().unique())" in text, "expected to find: " + ".addColumn('email', 'varchar(255)', (col) => col.notNull().unique())"[:80]

