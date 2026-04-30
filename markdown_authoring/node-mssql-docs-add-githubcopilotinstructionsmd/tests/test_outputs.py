"""Behavioral checks for node-mssql-docs-add-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/node-mssql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Commit messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/) enforced by commitlint. Semantic-release uses these to generate automated releases and changelogs, so correct' in text, "expected to find: " + '- **Commit messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/) enforced by commitlint. Semantic-release uses these to generate automated releases and changelogs, so correct'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Integration tests require a running SQL Server instance configured in `test/.mssql.json` (see `.devcontainer/.mssql.json` for the expected shape). The devcontainer sets up both Node.js and SQL Server ' in text, "expected to find: " + 'Integration tests require a running SQL Server instance configured in `test/.mssql.json` (see `.devcontainer/.mssql.json` for the expected shape). The devcontainer sets up both Node.js and SQL Server '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- **Integration tests** (`test/common/tests.js`): Exported as a factory `(sql, driver) => { ... }` — called by each driver's test file. Many tests exercise three execution styles: callback, promise, a" in text, "expected to find: " + "- **Integration tests** (`test/common/tests.js`): Exported as a factory `(sql, driver) => { ... }` — called by each driver's test file. Many tests exercise three execution styles: callback, promise, a"[:80]

