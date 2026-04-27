"""Behavioral tests for the OpenSearch SQL dialect.

The PR under test adds an OpenSearch dialect to Superset's sqlglot wrapper so
that double-quoted, mixed-case identifiers survive a SQLGlot round-trip
(MySQL's tokenizer would otherwise treat ``"`` as a string-literal delimiter
and emit ``'AvgTicketPrice'`` — a literal — instead of ``"AvgTicketPrice"`` —
an identifier).

Each ``test_*`` here corresponds 1:1 to a check id in eval_manifest.yaml.
"""
from __future__ import annotations

import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")


# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------
# The real superset package's __init__.py builds a Flask app, which would
# require flask-appbuilder, SQLAlchemy, redis, etc. Stub the top-level
# ``superset`` module so submodule imports resolve from disk without running
# the heavy init.
def _ensure_superset_stub() -> None:
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    if "superset" in sys.modules and not hasattr(sys.modules["superset"], "__path__"):
        del sys.modules["superset"]
    if "superset" not in sys.modules:
        stub = types.ModuleType("superset")
        stub.__path__ = [str(REPO / "superset")]
        sys.modules["superset"] = stub


_ensure_superset_stub()


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral
# ---------------------------------------------------------------------------
def test_opensearch_module_importable():
    """superset.sql.dialects.opensearch must define an OpenSearch class."""
    _ensure_superset_stub()
    from superset.sql.dialects.opensearch import OpenSearch  # noqa: F401

    from sqlglot.dialects.mysql import MySQL

    assert issubclass(OpenSearch, MySQL), (
        "OpenSearch dialect must subclass sqlglot's MySQL dialect — OpenSearch SQL is "
        "MySQL-compatible apart from identifier-quote handling."
    )


def test_double_quoted_identifier_roundtrip():
    """Double quotes must be tokenised as identifier delimiters, not strings.

    MySQL's default tokenizer treats ``"foo"`` as a string literal, so a SQL
    expression like ``SELECT "AvgTicketPrice" FROM "flights"`` round-trips as
    ``SELECT 'AvgTicketPrice' FROM 'flights'`` — i.e. the column name becomes
    a literal value. The OpenSearch dialect must preserve it as an identifier.
    """
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = 'SELECT "AvgTicketPrice" FROM "flights"'
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = 'SELECT\n  "AvgTicketPrice"\nFROM "flights"'
    assert out == expected, (
        f"Double-quoted identifiers must round-trip as identifiers.\n"
        f"  expected: {expected!r}\n  got: {out!r}"
    )


def test_single_quotes_still_strings():
    """Single quotes must continue to delimit string literals (MySQL behavior)."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = "SELECT * FROM flights WHERE Carrier = 'Kibana Airlines'"
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = (
        "SELECT\n  *\nFROM flights\nWHERE\n  Carrier = 'Kibana Airlines'"
    )
    assert out == expected, (
        f"Single-quoted string literals must NOT be reinterpreted as identifiers.\n"
        f"  expected: {expected!r}\n  got: {out!r}"
    )


def test_backtick_identifier_supported():
    """Backticks must also be accepted as identifier delimiters (MySQL-style)."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = "SELECT `AvgTicketPrice` FROM `flights`"
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    # sqlglot emits the dialect's first identifier-quote character on output.
    # OpenSearch lists '"' first, so backticks normalise to double quotes.
    expected = 'SELECT\n  "AvgTicketPrice"\nFROM "flights"'
    assert out == expected, (
        f"Backtick identifiers must parse and round-trip as identifiers.\n"
        f"  expected: {expected!r}\n  got: {out!r}"
    )


def test_mixed_quote_styles_roundtrip():
    """A query mixing both quote styles must produce a coherent identifier output."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = 'SELECT "AvgTicketPrice" AS `AvgTicketPrice` FROM `default`.`flights`'
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = (
        'SELECT\n  "AvgTicketPrice" AS "AvgTicketPrice"\n'
        'FROM "default"."flights"'
    )
    assert out == expected, (
        f"Mixed identifier quoting must round-trip cleanly.\n"
        f"  expected: {expected!r}\n  got: {out!r}"
    )


def test_in_clause_preserves_string_literals():
    """IN-clause string members must stay as strings (single-quote semantics intact)."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = "SELECT * FROM \"flights\" WHERE \"DestCountry\" IN ('US', 'CA', 'MX')"
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = (
        'SELECT\n  *\nFROM "flights"\nWHERE\n'
        '  "DestCountry" IN (\'US\', \'CA\', \'MX\')'
    )
    assert out == expected, f"\n  expected: {expected!r}\n  got: {out!r}"


def test_aggregate_with_quoted_identifiers():
    """Aggregates with quoted column args must compose with GROUP BY correctly."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = (
        'SELECT "Carrier", SUM("AvgTicketPrice") FROM "flights" GROUP BY "Carrier"'
    )
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = (
        'SELECT\n  "Carrier",\n  SUM("AvgTicketPrice")\n'
        'FROM "flights"\nGROUP BY\n  "Carrier"'
    )
    assert out == expected, f"\n  expected: {expected!r}\n  got: {out!r}"


def test_subquery_with_quoted_identifiers():
    """Quoted identifiers inside subqueries must remain identifiers."""
    _ensure_superset_stub()
    import sqlglot

    from superset.sql.dialects.opensearch import OpenSearch

    sql = 'SELECT * FROM (SELECT "Carrier", "AvgTicketPrice" FROM "flights") AS "sub"'
    ast = sqlglot.parse_one(sql, OpenSearch)
    out = OpenSearch().generate(expression=ast, pretty=True)

    expected = (
        'SELECT\n  *\n'
        'FROM (\n  SELECT\n    "Carrier",\n    "AvgTicketPrice"\n'
        '  FROM "flights"\n) AS "sub"'
    )
    assert out == expected, f"\n  expected: {expected!r}\n  got: {out!r}"


# ---------------------------------------------------------------------------
# Fail-to-pass: registration
# ---------------------------------------------------------------------------
def test_dialect_exported_from_package():
    """The dialect must be exported from superset.sql.dialects.__init__."""
    _ensure_superset_stub()
    import importlib

    # Drop a possibly-cached parent so the just-modified __init__ re-runs.
    for mod in list(sys.modules):
        if mod.startswith("superset.sql.dialects"):
            del sys.modules[mod]

    pkg = importlib.import_module("superset.sql.dialects")
    assert hasattr(pkg, "OpenSearch"), (
        "superset.sql.dialects must export OpenSearch (add it to "
        "the package's imports and __all__)."
    )

    from superset.sql.dialects.opensearch import OpenSearch as OS

    assert pkg.OpenSearch is OS, (
        "The OpenSearch re-exported by superset.sql.dialects must be the "
        "class defined in superset.sql.dialects.opensearch."
    )


def test_odelasticsearch_registered_in_parse_py():
    """parse.py must register OpenSearch as the sqlglot dialect for odelasticsearch.

    parse.py imports several heavy modules (jinja2, flask_babel, marshmallow,
    sqlglot.optimizer); under the test stub those are all installed. We import
    the real ``superset.sql.parse`` and check the SQLGLOT_DIALECTS map.
    """
    _ensure_superset_stub()
    import importlib

    for mod in list(sys.modules):
        if mod.startswith("superset.sql"):
            del sys.modules[mod]

    parse = importlib.import_module("superset.sql.parse")
    from superset.sql.dialects.opensearch import OpenSearch

    assert "odelasticsearch" in parse.SQLGLOT_DIALECTS, (
        "SQLGLOT_DIALECTS must contain the key 'odelasticsearch'."
    )
    assert parse.SQLGLOT_DIALECTS["odelasticsearch"] is OpenSearch, (
        "SQLGLOT_DIALECTS['odelasticsearch'] must be the OpenSearch class."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: existing dialects must still work
# ---------------------------------------------------------------------------
def test_existing_db2_dialect_still_exported():
    """The pre-existing DB2 / Dremio / Firebolt / Pinot exports must still resolve."""
    _ensure_superset_stub()
    import importlib

    for mod in list(sys.modules):
        if mod.startswith("superset.sql.dialects"):
            del sys.modules[mod]

    pkg = importlib.import_module("superset.sql.dialects")
    for name in ("DB2", "Dremio", "Firebolt", "FireboltOld", "Pinot"):
        assert hasattr(pkg, name), f"existing export {name} must remain available"


def test_existing_parse_py_mappings_intact():
    """The non-touched SQLGLOT_DIALECTS entries must still resolve correctly."""
    _ensure_superset_stub()
    import importlib

    for mod in list(sys.modules):
        if mod.startswith("superset.sql"):
            del sys.modules[mod]

    parse = importlib.import_module("superset.sql.parse")
    # A handful of pre-existing entries from the dict the agent must not break.
    assert "oceanbase" in parse.SQLGLOT_DIALECTS
    assert "oracle" in parse.SQLGLOT_DIALECTS
    assert "netezza" in parse.SQLGLOT_DIALECTS
    assert "pinot" in parse.SQLGLOT_DIALECTS


# ---------------------------------------------------------------------------
# Pass-to-pass: licence header & ruff / mypy if available
# ---------------------------------------------------------------------------
def test_new_dialect_file_has_asf_header():
    """AGENTS.md & CLAUDE.md require ASF licence headers on new source files."""
    target = REPO / "superset" / "sql" / "dialects" / "opensearch.py"
    if not target.exists():
        pytest.skip("OpenSearch module not yet created; skipped.")
    text = target.read_text()
    assert "Licensed to the Apache Software Foundation" in text, (
        "New Python files must carry the standard ASF licence header (see AGENTS.md)."
    )
    assert "Apache License, Version 2.0" in text, (
        "ASF header must reference the Apache License, Version 2.0."
    )


def test_repo_dialect_file_compiles():
    """The new dialect file must be syntactically valid Python."""
    target = REPO / "superset" / "sql" / "dialects" / "opensearch.py"
    if not target.exists():
        pytest.skip("OpenSearch module not yet created; skipped.")
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"
