"""Test outputs for the lancedb expression-builder PR scaffold.

Each `def test_*` function maps 1:1 to a check id in eval_manifest.yaml.

We exercise the new `lancedb::expr` module by writing Rust integration
tests into `rust/lancedb/tests/` and running `cargo test --test ...`
against the lancedb crate. cargo's exit code carries the result.

At the base commit:
  - `lancedb::expr::{col, lit, expr_to_sql_string, lower, upper, contains, func}`
    do not resolve, so the test binary fails to compile and `cargo test`
    exits non-zero.
At gold:
  - The imports resolve and the assertions pass.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/lancedb")
LANCEDB_CRATE = REPO / "rust" / "lancedb"
TESTS_DIR = LANCEDB_CRATE / "tests"
BUILDER_TEST_NAME = "expr_builder_harbor"
QUERY_TEST_NAME = "expr_query_harbor"
BUILDER_TEST_FILE = TESTS_DIR / f"{BUILDER_TEST_NAME}.rs"
QUERY_TEST_FILE = TESTS_DIR / f"{QUERY_TEST_NAME}.rs"

CARGO_ENV = {**os.environ, "CARGO_TERM_COLOR": "never", "RUST_BACKTRACE": "1"}

BUILDER_RS = r"""// Tests for the public expression-builder API in `lancedb::expr`.

use lancedb::expr::{col, contains, expr_to_sql_string, func, lit, lower, upper};

#[test]
fn test_col_lit_gt_to_sql() {
    let expr = col("age").gt(lit(18));
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.contains("age"), "missing column name 'age' in SQL: {}", sql);
    assert!(sql.contains("18"), "missing literal '18' in SQL: {}", sql);
    assert!(sql.contains(">"), "missing '>' operator in SQL: {}", sql);
}

#[test]
fn test_col_lit_eq_string() {
    let expr = col("name").eq(lit("Alice"));
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.contains("name"), "missing 'name' in SQL: {}", sql);
    assert!(sql.contains("Alice"), "missing 'Alice' in SQL: {}", sql);
}

#[test]
fn test_compound_and_expression() {
    let expr = col("age").gt(lit(18)).and(col("status").eq(lit("active")));
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.contains("age") && sql.contains("18"),
            "SQL missing age/18: {}", sql);
    assert!(sql.contains("status") && sql.contains("active"),
            "SQL missing status/active: {}", sql);
    let up = sql.to_uppercase();
    assert!(up.contains(" AND "), "SQL missing AND keyword: {}", sql);
}

#[test]
fn test_or_combinator() {
    let expr = col("a").lt(lit(5)).or(col("b").gt(lit(10)));
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.contains("a") && sql.contains("5"));
    assert!(sql.contains("b") && sql.contains("10"));
    assert!(sql.to_uppercase().contains(" OR "), "SQL missing OR keyword: {}", sql);
}

#[test]
fn test_lower_and_upper_string_functions() {
    let s_lower = expr_to_sql_string(&lower(col("name"))).unwrap();
    assert!(s_lower.to_lowercase().contains("lower"),
            "SQL missing lower(): {}", s_lower);
    assert!(s_lower.contains("name"), "SQL missing column 'name': {}", s_lower);

    let s_upper = expr_to_sql_string(&upper(col("name"))).unwrap();
    assert!(s_upper.to_lowercase().contains("upper"),
            "SQL missing upper(): {}", s_upper);
    assert!(s_upper.contains("name"), "SQL missing column 'name': {}", s_upper);
}

#[test]
fn test_contains_string_function() {
    let expr = contains(col("text"), lit("search"));
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.to_lowercase().contains("contains"),
            "SQL missing contains(): {}", sql);
    assert!(sql.contains("text"), "missing 'text': {}", sql);
    assert!(sql.contains("search"), "missing 'search': {}", sql);
}

#[test]
fn test_func_known_returns_ok() {
    let expr = func("lower", vec![col("x")]).expect("known function should resolve");
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.to_lowercase().contains("lower"));

    let expr = func("upper", vec![col("y")]).expect("known function should resolve");
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.to_lowercase().contains("upper"));

    let expr = func("contains", vec![col("z"), lit("foo")])
        .expect("known function should resolve");
    let sql = expr_to_sql_string(&expr).unwrap();
    assert!(sql.to_lowercase().contains("contains"));
}

#[test]
fn test_func_unknown_returns_err() {
    let result = func("totally_unknown_function_xyz", vec![col("x")]);
    assert!(result.is_err(),
            "expected unknown function name to return Err, got Ok");
}
"""

QUERY_RS = r"""// Compile-time + runtime check that `QueryBase::only_if_expr` is added.

use lancedb::expr::{col, lit};

#[allow(dead_code)]
fn _typecheck_only_if_expr<Q>(q: Q) -> Q
where
    Q: lancedb::query::QueryBase,
{
    // If `only_if_expr` is not part of the QueryBase trait, this function
    // fails to compile, the test binary fails to link, and the cargo test
    // run exits non-zero.
    q.only_if_expr(col("x").gt(lit(10)))
}

#[test]
fn test_only_if_expr_trait_method_compiles() {
    // Compilation is the assertion. Body is a runtime no-op so the test
    // is registered as a passing run by libtest.
    let f: fn(()) -> () = |_| {};
    f(());
}
"""


@pytest.fixture(autouse=True)
def _ensure_no_stale_harbor_tests():
    """Remove any leftover harbor *.rs files before/after each test.

    Keeps the p2p tests that run `cargo check`/`cargo test --lib` from
    being influenced by integration tests we install for the f2p checks.
    """
    for f in (BUILDER_TEST_FILE, QUERY_TEST_FILE):
        f.unlink(missing_ok=True)
    yield
    for f in (BUILDER_TEST_FILE, QUERY_TEST_FILE):
        f.unlink(missing_ok=True)


def _run_cargo_test(test_name: str, source: str) -> subprocess.CompletedProcess:
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    (TESTS_DIR / f"{test_name}.rs").write_text(source)
    return subprocess.run(
        ["cargo", "test",
         "-p", "lancedb",
         "--test", test_name,
         "--",
         "--nocapture"],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=1500,
    )


# ---------------------------------------------------------------------------
# pass-to-pass tests run first.
# ---------------------------------------------------------------------------

def test_lancedb_compiles():
    """`cargo check -p lancedb` still succeeds (compilation regression).

    Library-only check (no `--tests`) so this stays a pure p2p: the
    integration tests we copy in for the f2p checks below do not affect
    this run.
    """
    r = subprocess.run(
        ["cargo", "check", "--quiet", "-p", "lancedb"],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=1500,
    )
    tail = (r.stderr or "")[-2000:]
    assert r.returncode == 0, f"cargo check failed (rc={r.returncode}):\n{tail}"


def test_existing_only_if_unit_test_still_passes():
    """The pre-existing `only_if` SQL string filter codepath still works.

    Runs the lancedb crate's own unit test that exercises the
    `only_if(<sql_string>)` API on a local NativeTable. `cargo test --lib`
    only compiles in-source unit tests, so this is unaffected by anything
    we may copy into `tests/`.
    """
    r = subprocess.run(
        ["cargo", "test", "--quiet",
         "-p", "lancedb",
         "--lib",
         "query::tests::test_execute_no_vector",
         "--",
         "--exact"],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=1500,
    )
    tail = (r.stdout or "")[-1500:] + "\n---STDERR---\n" + (r.stderr or "")[-1500:]
    assert r.returncode == 0, f"only_if regression test failed:\n{tail}"


# ---------------------------------------------------------------------------
# fail-to-pass: split across two independent integration-test binaries.
# ---------------------------------------------------------------------------

def test_expr_builder_api():
    """The public `lancedb::expr` builder API: col/lit/lower/upper/contains/func/expr_to_sql_string."""
    r = _run_cargo_test(BUILDER_TEST_NAME, BUILDER_RS)
    tail = (r.stdout or "")[-2500:] + "\n---STDERR---\n" + (r.stderr or "")[-2500:]
    assert r.returncode == 0, (
        f"expr_builder cargo test failed (rc={r.returncode}):\n{tail}"
    )


def test_only_if_expr_trait_method_exists():
    """`QueryBase::only_if_expr(self, datafusion_expr::Expr) -> Self` exists.

    The Rust test binary uses a generic helper that calls `only_if_expr`
    on any `Q: QueryBase`. If the trait method is missing, the binary
    fails to compile and `cargo test` exits non-zero.
    """
    r = _run_cargo_test(QUERY_TEST_NAME, QUERY_RS)
    tail = (r.stdout or "")[-2000:] + "\n---STDERR---\n" + (r.stderr or "")[-2000:]
    assert r.returncode == 0, (
        f"expr_query cargo test failed (rc={r.returncode}):\n{tail}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_format_check():
    """pass_to_pass | CI job 'Lint' → step 'Format check'"""
    r = subprocess.run(
        ["bash", "-lc", 'ruff format --check .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_lint():
    """pass_to_pass | CI job 'Lint' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'ruff check .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_python():
    """pass_to_pass | CI job 'build' → step 'Build Python'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m pip install --extra-index-url https://pypi.fury.io/lance-format/ --extra-index-url https://pypi.fury.io/lancedb/ -e . && python -m pip install --extra-index-url https://pypi.fury.io/lance-format/ --extra-index-url https://pypi.fury.io/lancedb/ -r ../docs/requirements.txt'], cwd=os.path.join(REPO, 'python'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Python' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_no_lock_build_all():
    """pass_to_pass | CI job 'build-no-lock' → step 'Build all'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build --profile ci --benches --all-features --tests'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_run_format():
    """pass_to_pass | CI job 'lint' → step 'Run format'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fmt --all -- --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_run_clippy():
    """pass_to_pass | CI job 'lint' → step 'Run clippy'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo clippy --profile ci --workspace --tests --all-features -- -D warnings'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_run_clippy_without_remote_feature():
    """pass_to_pass | CI job 'lint' → step 'Run clippy (without remote feature)'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo clippy --profile ci --workspace --tests -- -D warnings'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy (without remote feature)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")