"""
Task: prql-fix-return-error-for-join
Repo: PRQL/prql @ 76deaddd5dbbe8548672777ed5a4d6ac10d92171
PR:   5587

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/prql")
GEN_QUERY_FILE = REPO / "prqlc" / "prqlc" / "src" / "sql" / "gen_query.rs"

# Rust tests injected into gen_query.rs to exercise the join-inside-group fix.
# On the base commit, compile() panics due to .unwrap() on None.
# After fix, compile() returns Err with a helpful message.
RUST_TESTS = textwrap.dedent("""\

#[cfg(test)]
mod _harbor_join_scope_tests {
    #[test]
    fn join_inside_group_returns_error() {
        let query = r#"
        from c = companies
        join ca = companies_addresses (c.tax_code == ca.company)
        group c.tax_code (
          join a = addresses (a.id == ca.address)
          sort {-ca.created_at}
          take 2..
        )
        sort tax_code
        "#;
        let result = crate::tests::compile(query);
        assert!(result.is_err(), "join inside group should return an error, not succeed or panic");
    }

    #[test]
    fn join_inside_group_error_mentions_context() {
        let query = r#"
        from c = companies
        join ca = companies_addresses (c.tax_code == ca.company)
        group c.tax_code (
          join a = addresses (a.id == ca.address)
          sort {-ca.created_at}
          take 2..
        )
        sort tax_code
        "#;
        let err = crate::tests::compile(query).unwrap_err().to_string();
        let lower = err.to_lowercase();
        assert!(
            lower.contains("accessible") || lower.contains("scope") || lower.contains("context") || lower.contains("group"),
            "error should explain why the join fails, got: {}", err
        );
    }
}
""")


@pytest.fixture(scope="session", autouse=True)
def inject_rust_tests():
    """Inject Rust test module into gen_query.rs for join scope tests."""
    original = GEN_QUERY_FILE.read_text()
    GEN_QUERY_FILE.write_text(original + RUST_TESTS)
    subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--no-run"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    yield
    GEN_QUERY_FILE.write_text(original)


@pytest.fixture(scope="session")
def rust_test_results(inject_rust_tests):
    """Run all harbor join scope Rust tests in a single cargo invocation."""
    return subprocess.run(
        ["cargo", "test", "-p", "prqlc", "--", "_harbor_join_scope_tests"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )


def _assert_rust_test_passed(results: subprocess.CompletedProcess, test_name: str):
    """Assert a specific Rust test passed in the batch results."""
    combined = results.stdout + results.stderr
    if f"{test_name} ... ok" in combined:
        return
    assert False, (
        f"Rust test '{test_name}' did not pass.\n"
        f"stdout:\n{results.stdout}\nstderr:\n{results.stderr}"
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — crate must compile
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """The prqlc crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "prqlc"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_join_group_returns_error(rust_test_results):
    """Join inside group clause must return an error instead of panicking."""
    _assert_rust_test_passed(rust_test_results, "join_inside_group_returns_error")


# [pr_diff] fail_to_pass
def test_error_mentions_context(rust_test_results):
    """Error message must explain why the join fails (scope/context/group)."""
    _assert_rust_test_passed(rust_test_results, "join_inside_group_error_mentions_context")


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — CLAUDE.md:103-108 @ 75d6b8b2


# [config_edit] fail_to_pass — CLAUDE.md:103-108 @ 75d6b8b2


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — existing tests still pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_gen_query_tests():
    """Existing prqlc gen_query tests must not regress."""
    # Strip injected test module so upstream tests run cleanly
    content = GEN_QUERY_FILE.read_text()
    marker = "\n#[cfg(test)]\nmod _harbor_join_scope_tests {"
    if marker in content:
        clean = content[:content.index(marker)] + "\n"
        GEN_QUERY_FILE.write_text(clean)
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "prqlc", "--", "gen_query::test"],
            cwd=REPO, capture_output=True, text=True, timeout=300,
        )
        assert r.returncode == 0, f"Existing tests failed:\n{r.stdout}\n{r.stderr}"
    finally:
        GEN_QUERY_FILE.write_text(content)
