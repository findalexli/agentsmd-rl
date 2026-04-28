"""Behavioral checks for copilot-collections-chore-add-suggestion-around-online (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-collections")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sql-and-database/SKILL.md')
    assert '| **Database support** | `CONCURRENTLY` is PostgreSQL-specific. Other engines have their own online indexing alternatives: MySQL/MariaDB use `ALGORITHM=INPLACE, LOCK=NONE`; SQL Server uses `WITH (ONLI' in text, "expected to find: " + '| **Database support** | `CONCURRENTLY` is PostgreSQL-specific. Other engines have their own online indexing alternatives: MySQL/MariaDB use `ALGORITHM=INPLACE, LOCK=NONE`; SQL Server uses `WITH (ONLI'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sql-and-database/SKILL.md')
    assert '| **Migration frameworks** | Most migration tools wrap statements in a transaction by default. Disable this for concurrent index operations (e.g., `disable_ddl_transaction!` in Rails, `atomic = False`' in text, "expected to find: " + '| **Migration frameworks** | Most migration tools wrap statements in a transaction by default. Disable this for concurrent index operations (e.g., `disable_ddl_transaction!` in Rails, `atomic = False`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sql-and-database/SKILL.md')
    assert 'Standard `CREATE INDEX` and `DROP INDEX` acquire locks that **block writes** on the table for the duration of the operation. On large or heavily-used tables this can cause downtime.' in text, "expected to find: " + 'Standard `CREATE INDEX` and `DROP INDEX` acquire locks that **block writes** on the table for the duration of the operation. On large or heavily-used tables this can cause downtime.'[:80]

