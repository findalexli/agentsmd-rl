"""
Task: prql-fix-distinct-on-to-include
Repo: PRQL/prql @ 7b0d983ead8d91921252ad835a3c43b2288b7fe1
PR:   5562

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/prql"


@pytest.fixture(scope="module")
def prqlc_binary():
    """Build prqlc once and return path to the debug binary."""
    r = subprocess.run(
        ["cargo", "build", "-p", "prqlc"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo build -p prqlc failed:\n{r.stderr.decode()}"
    binary = Path(REPO) / "target" / "debug" / "prqlc"
    assert binary.exists(), f"Binary not found at {binary}"
    return str(binary)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust files must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "prqlc"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — repo CI clippy linting passes
def test_repo_clippy():
    """Repo clippy linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "prqlc", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo CI formatting check passes
def test_repo_fmt():
    """Repo rustfmt formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo lib tests for prqlc pass
def test_repo_prqlc_lib_tests():
    """Repo prqlc lib tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--no-default-features", "--features=default", "--lib", "--quiet"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"prqlc lib tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo integration tests for prqlc pass
def test_repo_prqlc_integration_tests():
    """Repo prqlc integration tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--no-default-features", "--features=default", "--test", "integration", "--quiet"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"prqlc integration tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — gen_query unit tests (covers modified file)
def test_repo_gen_query_tests():
    """Repo gen_query unit tests pass (pass_to_pass) — covers modified gen_query.rs."""
    r = subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--no-default-features", "--features=default", "--lib", "--", "gen_query"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"gen_query tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — distinct_on integration tests (related to PR)
def test_repo_distinct_on_tests():
    """Repo DISTINCT ON integration tests pass (pass_to_pass) — covers the bug fix area."""
    r = subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--no-default-features", "--features=default", "--", "sql::test_distinct_on"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"DISTINCT ON tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — prqlc-parser checks (dependency of modified code)
def test_repo_prqlc_parser_check():
    """Repo prqlc-parser crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "prqlc-parser"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"prqlc-parser check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_distinct_on_wildcard(prqlc_binary):
    """DISTINCT ON with group/take + select on DuckDB must produce * not NULL."""
    query = (
        "prql target:sql.duckdb\n\n"
        "from tab1\n"
        "group col1 (take 1)\n"
        "derive foo = 1\n"
        "select foo\n"
    )
    r = subprocess.run(
        [prqlc_binary, "compile"],
        input=query, cwd=REPO, capture_output=True, timeout=60, text=True,
    )
    assert r.returncode == 0, f"prqlc compile failed:\n{r.stderr}"
    sql = r.stdout
    assert "DISTINCT ON" in sql, f"Expected DISTINCT ON in output:\n{sql}"
    assert "NULL" not in sql, (
        f"DISTINCT ON output must not contain NULL:\n{sql}"
    )
    assert "DISTINCT ON (col1) *" in sql, (
        f"DISTINCT ON should have wildcard *, got:\n{sql}"
    )


# [pr_diff] fail_to_pass
def test_distinct_on_aggregate_wildcard(prqlc_binary):
    """DISTINCT ON with group/take + aggregate on PostgreSQL must produce * not empty projection."""
    query = (
        "prql target:sql.postgres\n\n"
        "from t1\n"
        "group {id, name} (take 1)\n"
        "aggregate {c = count this}\n"
    )
    r = subprocess.run(
        [prqlc_binary, "compile"],
        input=query, cwd=REPO, capture_output=True, timeout=60, text=True,
    )
    assert r.returncode == 0, f"prqlc compile failed:\n{r.stderr}"
    sql = r.stdout
    assert "DISTINCT ON" in sql, f"Expected DISTINCT ON in SQL:\n{sql}"
    # Between DISTINCT ON and FROM, must have * wildcard
    distinct_to_from = sql.split("DISTINCT ON")[1].split("FROM")[0]
    assert "*" in distinct_to_from, (
        f"DISTINCT ON projection must contain wildcard *, got:\n{sql}"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — CLAUDE.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
