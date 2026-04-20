"""
Test suite for quickwit-oss/quickwit#6097 - TermsQuery numeric support.

This tests that TermsQuery can accept numeric values (i64, u64) in addition to strings.
"""

import subprocess
import os
import pytest

REPO = "/workspace/quickwit/quickwit"


def test_terms_query_numeric_array():
    """TermsQuery accepts integer arrays like [1, 2] and converts them to strings.

    Fails on base commit (test does not exist). Passes on fixed commit.
    """
    # Run the specific test that was added by the PR
    r = subprocess.run(
        ["cargo", "test", "-p", "quickwit-query", "--lib", "test_terms_query_not_string", "--", "--nocapture"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "RUST_BACKTRACE": "1"}
    )
    # The test should exist and pass after the fix
    assert r.returncode == 0, f"Test failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr[-2000:]}"
    assert "test_terms_query_not_string" in r.stdout, "Test was not run"


def test_terms_query_single_numeric():
    """TermsQuery accepts a single integer value like 123 and converts it to "123".

    Passes on both base commit and fixed commit (existing functionality).
    """
    # Run a test that verifies single numeric term parsing
    r = subprocess.run(
        ["cargo", "test", "-p", "quickwit-query", "--lib", "test_terms_query_single_term", "--", "--nocapture"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "RUST_BACKTRACE": "1"}
    )
    assert r.returncode == 0, f"Test failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr[-2000:]}"


def test_terms_query_build():
    """The quickwit-query crate compiles successfully with the fix.

    Fails on base commit if fix breaks compilation. Passes on fixed commit.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "quickwit-query"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\nSTDERR:\n{r.stderr[-2000:]}"


def test_terms_query_all_tests():
    """All TermsQuery library tests pass with the fix.

    Ensures no regressions in existing functionality.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "quickwit-query", "--lib", "elastic_query_dsl::terms_query"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "RUST_BACKTRACE": "1"}
    )
    # Check for test failures
    assert r.returncode == 0, f"Tests failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr[-2000:]}"


def test_repo_clippy():
    """Clippy passes on quickwit-query crate (pass_to_pass).

    Runs actual CI lint command.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "quickwit-query", "--all-features", "--", "-Dwarnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Clippy failed:\nSTDERR:\n{r.stderr[-2000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
