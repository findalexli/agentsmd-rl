"""Behavioral tests for the word-cloud buildQuery fix (apache/superset#39073).

The runner at /harness/run_buildquery.ts loads the buildQuery TypeScript source
through tsx (with hand-rolled stubs for @superset-ui/core / @apache-superset/core
under /node_modules), exercises it with several formData inputs, and emits a
JSON object describing the resulting orderby / columns for each case. These
Python tests parse that JSON and assert on the observable behavior.
"""
from __future__ import annotations

import functools
import json
import subprocess
from pathlib import Path

HARNESS = Path("/harness")
RUNNER = HARNESS / "run_buildquery.ts"


@functools.lru_cache(maxsize=1)
def runner_output() -> dict:
    """Invoke the TS runner once and cache its parsed JSON output."""
    proc = subprocess.run(
        ["tsx", str(RUNNER)],
        cwd=str(HARNESS),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"Harness failed (rc={proc.returncode}):\n"
        f"--- stdout ---\n{proc.stdout[-2000:]}\n"
        f"--- stderr ---\n{proc.stderr[-2000:]}"
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Harness produced non-JSON output:\n{proc.stdout[-2000:]}\n"
            f"stderr: {proc.stderr[-2000:]}"
        ) from exc


# ---------- f2p (fail at base, pass at gold) ----------


def test_no_sort_omits_orderby():
    """When neither sort_by_metric nor sort_by_series is enabled, the query must
    NOT include any orderby clause — even when 'series' is set. Adding a
    series sort unconditionally forces a multi-column ORDER BY, which on Druid
    prevents the native TopN optimization.
    """
    out = runner_output()
    case = out["no_sort"]
    assert case["orderby"] is None, (
        f"Expected no orderby when both sort flags are false, "
        f"got {case['orderby']!r}"
    )


def test_metric_only_orderby():
    """With sort_by_metric=true and sort_by_series=false, orderby must contain
    ONLY the metric sort — no implicit secondary series tiebreaker. The
    secondary series sort is what defeats Druid's TopN optimization.
    """
    out = runner_output()
    case = out["metric_only"]
    assert case["orderby"] == [["count", False]], (
        f"Expected orderby == [['count', False]] (metric DESC only), "
        f"got {case['orderby']!r}"
    )


def test_metric_only_orderby_high_cardinality():
    """Same contract under different metric/series/row_limit values, to guard
    against fixes that hardcode 'count' or 'foo'.
    """
    out = runner_output()
    case = out["high_cardinality_metric"]
    assert case["orderby"] == [["sum_population", False]], (
        f"Expected orderby == [['sum_population', False]], "
        f"got {case['orderby']!r}"
    )


# ---------- p2p (pass at base AND gold) ----------


def test_series_only_orderby():
    """With sort_by_series=true, orderby must include the series ASC sort."""
    out = runner_output()
    case = out["series_only"]
    assert case["orderby"] == [["foo", True]], (
        f"Expected orderby == [['foo', True]] (series ASC only), "
        f"got {case['orderby']!r}"
    )


def test_both_sorts_orderby():
    """With both sort flags enabled, orderby must contain metric DESC then
    series ASC, in that order.
    """
    out = runner_output()
    case = out["both_sorts"]
    assert case["orderby"] == [["count", False], ["foo", True]], (
        f"Expected orderby == [['count', False], ['foo', True]], "
        f"got {case['orderby']!r}"
    )


def test_existing_columns_check():
    """Pre-existing test contract: query.columns must come from formData.series.
    This must continue to pass — the fix should not regress it.
    """
    out = runner_output()
    case = out["columns_check"]
    assert case["columns"] == ["foo"], (
        f"Expected columns == ['foo'], got {case['columns']!r}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_sqlite_python_integration_tests_sqlite():
    """pass_to_pass | CI job 'test-sqlite' → step 'Python integration tests (SQLite)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (SQLite)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_build_columns_from_series_in_form_data():
    """fail_to_pass | PR added test 'should build columns from series in form data' in 'superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should build columns from series in form data" 2>&1 || npx vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should build columns from series in form data" 2>&1 || pnpm jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should build columns from series in form data" 2>&1 || npx jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should build columns from series in form data" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should build columns from series in form data' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_not_include_orderby_when_neither_sort_opt():
    """fail_to_pass | PR added test 'should not include orderby when neither sort option is enabled' in 'superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should not include orderby when neither sort option is enabled" 2>&1 || npx vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should not include orderby when neither sort option is enabled" 2>&1 || pnpm jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should not include orderby when neither sort option is enabled" 2>&1 || npx jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should not include orderby when neither sort option is enabled" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should not include orderby when neither sort option is enabled' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_order_by_metric_DESC_only_when_sort_by_me():
    """fail_to_pass | PR added test 'should order by metric DESC only when sort_by_metric is true' in 'superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC only when sort_by_metric is true" 2>&1 || npx vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC only when sort_by_metric is true" 2>&1 || pnpm jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC only when sort_by_metric is true" 2>&1 || npx jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC only when sort_by_metric is true" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should order by metric DESC only when sort_by_metric is true' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_order_by_series_ASC_only_when_sort_by_ser():
    """fail_to_pass | PR added test 'should order by series ASC only when sort_by_series is true' in 'superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by series ASC only when sort_by_series is true" 2>&1 || npx vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by series ASC only when sort_by_series is true" 2>&1 || pnpm jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by series ASC only when sort_by_series is true" 2>&1 || npx jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by series ASC only when sort_by_series is true" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should order by series ASC only when sort_by_series is true' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_order_by_metric_DESC_then_series_ASC_when():
    """fail_to_pass | PR added test 'should order by metric DESC then series ASC when both are true' in 'superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC then series ASC when both are true" 2>&1 || npx vitest run "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC then series ASC when both are true" 2>&1 || pnpm jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC then series ASC when both are true" 2>&1 || npx jest "superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts" -t "should order by metric DESC then series ASC when both are true" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should order by metric DESC then series ASC when both are true' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
