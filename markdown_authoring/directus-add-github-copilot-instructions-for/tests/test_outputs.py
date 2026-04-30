"""Behavioral checks for directus-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/directus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Directus is a real-time API and App dashboard for managing SQL database content. It's a monorepo that includes:" in text, "expected to find: " + "Directus is a real-time API and App dashboard for managing SQL database content. It's a monorepo that includes:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Directus is licensed under BUSL-1.1 (Business Source License). Review the license file before contributing.' in text, "expected to find: " + 'Directus is licensed under BUSL-1.1 (Business Source License). Review the license file before contributing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Database Support**: PostgreSQL, MySQL, SQLite, OracleDB, CockroachDB, MariaDB, MS-SQL' in text, "expected to find: " + '- **Database Support**: PostgreSQL, MySQL, SQLite, OracleDB, CockroachDB, MariaDB, MS-SQL'[:80]

