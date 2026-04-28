"""Tests for the Firebolt SQLGlot dialect EXCLUDE / EXCEPT fix.

The Firebolt Generator inherits from sqlglot.generator.Generator, whose default
star-except keyword is ``EXCEPT``. Firebolt SQL grammar uses ``EXCLUDE``
(like DuckDB and Snowflake), so passing ``SELECT * EXCLUDE (col)`` through
sqlglot with the firebolt dialect must round-trip with EXCLUDE preserved.

The dialect file at superset/sql/dialects/firebolt.py imports only sqlglot,
so we load it directly via importlib (bypassing the heavy ``superset``
package __init__) — the metaclass on sqlglot ``Dialect`` registers
``firebolt`` as a known dialect on import.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/superset")
FIREBOLT_PATH = REPO / "superset" / "sql" / "dialects" / "firebolt.py"


def _load_firebolt():
    cached = sys.modules.get("firebolt_dialect_under_test")
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(
        "firebolt_dialect_under_test", str(FIREBOLT_PATH)
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["firebolt_dialect_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _format(sql: str) -> str:
    """Parse `sql` with the firebolt dialect and re-render as firebolt SQL."""
    import sqlglot

    _load_firebolt()
    parsed = sqlglot.parse_one(sql, dialect="firebolt")
    return parsed.sql(dialect="firebolt")


# ---------------------------------------------------------------------------
# fail_to_pass: EXCLUDE must round-trip as EXCLUDE, not EXCEPT.
# ---------------------------------------------------------------------------


def test_firebolt_exclude_single_column_with_alias():
    """The original bug report: ``SELECT g.* EXCLUDE (col) FROM t g``."""
    out = _format(
        "SELECT g.* EXCLUDE (source_file_timestamp) FROM public.games g"
    )
    assert "EXCLUDE" in out, f"EXCLUDE missing from generated SQL: {out!r}"
    assert "EXCEPT" not in out, (
        f"EXCEPT must NOT appear in generated SQL: {out!r}"
    )
    assert "source_file_timestamp" in out


def test_firebolt_exclude_multiple_columns():
    out = _format("SELECT * EXCLUDE (col1, col2, col3) FROM my_table")
    assert "EXCLUDE" in out, f"EXCLUDE missing: {out!r}"
    assert "EXCEPT" not in out, f"EXCEPT must not appear: {out!r}"
    for col in ("col1", "col2", "col3"):
        assert col in out, f"Column {col} missing from output {out!r}"


def test_firebolt_exclude_two_columns():
    """A second variation of EXCLUDE with two columns and a table alias."""
    out = _format("SELECT t.* EXCLUDE (a, b) FROM tbl t")
    assert "EXCLUDE" in out
    assert "EXCEPT" not in out
    assert "a" in out and "b" in out


# ---------------------------------------------------------------------------
# pass_to_pass: pre-existing Firebolt dialect behavior must keep working.
# ---------------------------------------------------------------------------


def test_firebolt_not_in_parenthesized():
    """Firebolt dialect parenthesizes negated IN expressions (pre-existing)."""
    out = _format("SELECT * FROM my_table WHERE id NOT IN (1, 2, 3)")
    assert "NOT (" in out, (
        f"Firebolt should wrap NOT IN in parentheses: {out!r}"
    )


def test_firebolt_basic_select_parses():
    out = _format("SELECT * FROM my_table LIMIT 10")
    upper = out.upper()
    assert "SELECT" in upper
    assert "MY_TABLE" in upper
    assert "10" in out


def test_firebolt_module_loads_cleanly():
    mod = _load_firebolt()
    assert hasattr(mod, "Firebolt")
    assert hasattr(mod, "FireboltOld")


def test_firebolt_dialect_is_registered_with_sqlglot():
    """Loading the module must register firebolt as a known sqlglot dialect."""
    import sqlglot
    from sqlglot.dialects.dialect import Dialect

    _load_firebolt()
    # parse_one should accept dialect="firebolt" without raising.
    sqlglot.parse_one("SELECT 1", dialect="firebolt")
    cls = Dialect.get_or_raise("firebolt")
    assert cls is not None


def test_firebolt_python_module_compiles():
    """The patched firebolt.py must remain importable / syntactically valid."""
    r = subprocess.run(
        [sys.executable, "-c", "import py_compile, sys; py_compile.compile(sys.argv[1], doraise=True)", str(FIREBOLT_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Failed to compile {FIREBOLT_PATH}:\nstdout={r.stdout}\nstderr={r.stderr}"
    )


# ---------------------------------------------------------------------------
# CI/CD scoped regression test: run the existing Firebolt dialect unit tests
# via pytest as a pass_to_pass guard.
# ---------------------------------------------------------------------------


def test_ci_firebolt_dialect_unit_tests():
    """pass_to_pass | Run the Firebolt dialect unit test suite via pytest (scoped regression)."""
    r = subprocess.run(
        ["bash", "-lc",
         "pip install -e . >/dev/null 2>&1 && python -m pytest tests/unit_tests/sql/dialects/firebolt_tests.py -v --tb=short --noconftest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Firebolt dialect unit tests failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )
