"""Behavioral checks for eparse-add-copilot-instructions-to-eparse (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eparse")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- AUTHORS.rst, CONTRIBUTING.rst, HISTORY.rst, LICENSE, MANIFEST.in, Makefile, README.rst, pyproject.toml, setup.cfg, tox.ini, .pre-commit-config.yaml, .github/, eparse/, tests/, docs/, contrib/' in text, "expected to find: " + '- AUTHORS.rst, CONTRIBUTING.rst, HISTORY.rst, LICENSE, MANIFEST.in, Makefile, README.rst, pyproject.toml, setup.cfg, tox.ini, .pre-commit-config.yaml, .github/, eparse/, tests/, docs/, contrib/'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Purpose:** eparse is a Python package and CLI tool for crawling, parsing, and extracting tabular data from Excel spreadsheets, with support for SQLite and PostgreSQL outputs.' in text, "expected to find: " + '- **Purpose:** eparse is a Python package and CLI tool for crawling, parsing, and extracting tabular data from Excel spreadsheets, with support for SQLite and PostgreSQL outputs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Config: `pyproject.toml`, `setup.cfg`, `tox.ini`, `.pre-commit-config.yaml`, `Makefile`' in text, "expected to find: " + '- Config: `pyproject.toml`, `setup.cfg`, `tox.ini`, `.pre-commit-config.yaml`, `Makefile`'[:80]

