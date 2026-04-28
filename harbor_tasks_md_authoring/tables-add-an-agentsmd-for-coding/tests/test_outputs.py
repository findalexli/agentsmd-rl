"""Behavioral checks for tables-add-an-agentsmd-for-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tables")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Supports PostgreSQL, MySQL, and SQLite. The unusual design detail is that row cell values are stored in **per-type tables** (`tables_row_cells_text`, `tables_row_cells_number`, `tables_row_cells_datet' in text, "expected to find: " + 'Supports PostgreSQL, MySQL, and SQLite. The unusual design detail is that row cell values are stored in **per-type tables** (`tables_row_cells_text`, `tables_row_cells_number`, `tables_row_cells_datet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Nextcloud Tables** is a Nextcloud app (PHP backend + Vue.js frontend) that lets users create and manage custom data tables with typed columns, views, sharing, and import/export. It ships a full OCS ' in text, "expected to find: " + '**Nextcloud Tables** is a Nextcloud app (PHP backend + Vue.js frontend) that lets users create and manage custom data tables with typed columns, views, sharing, and import/export. It ships a full OCS '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`lib/Controller/`** — OCS REST API controllers. `Api1Controller.php` is the monolithic v1 handler; newer controllers (e.g. `ApiTablesController`, `ContextController`) are split by resource type. P' in text, "expected to find: " + '- **`lib/Controller/`** — OCS REST API controllers. `Api1Controller.php` is the monolithic v1 handler; newer controllers (e.g. `ApiTablesController`, `ContextController`) are split by resource type. P'[:80]

