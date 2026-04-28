"""Behavioral checks for analytics-toolbox-core-choreora-codify-oracle-typing-convent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/analytics-toolbox-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert 'Individual test modules (`test_*.py`) must not use `sys.path.insert(...)` or `from run_query import run_query`. These patterns are bootstrap-level infrastructure and belong only in `__init__.py` packa' in text, "expected to find: " + 'Individual test modules (`test_*.py`) must not use `sys.path.insert(...)` or `from run_query import run_query`. These patterns are bootstrap-level infrastructure and belong only in `__init__.py` packa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert 'Shared types (used by multiple functions in a module) go in a dedicated `00_<type_name>.sql` file — the `00_` prefix ensures alphabetical deploy ordering (types before functions that consume them). Mo' in text, "expected to find: " + 'Shared types (used by multiple functions in a module) go in a dedicated `00_<type_name>.sql` file — the `00_` prefix ensures alphabetical deploy ordering (types before functions that consume them). Mo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert 'Data exits Oracle as JSON only at the Gateway HTTP wire. Collections serialize to JSON CLOB there; SQL-native Oracle callers never see raw JSON. `INTERNAL_GENERIC_HTTP`, `INTERNAL_CREATE_BUILDER_MAP`,' in text, "expected to find: " + 'Data exits Oracle as JSON only at the Gateway HTTP wire. Collections serialize to JSON CLOB there; SQL-native Oracle callers never see raw JSON. `INTERNAL_GENERIC_HTTP`, `INTERNAL_CREATE_BUILDER_MAP`,'[:80]

