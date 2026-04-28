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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_python_integration_tests_mysql():
    """pass_to_pass | CI job 'test-mysql' → step 'Python integration tests (MySQL)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (MySQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run ci:release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_frontend_check_translations_lint():
    """pass_to_pass | CI job 'frontend-check-translations' → step 'lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build-translation'], cwd=os.path.join(REPO, './superset-frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")