"""
Task: remix-remove-router-run
Repo: remix-run/remix @ 783fa46240191001e0ee2084297b5c81d78b3545
PR:   11071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code removal tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_run_method_removed():
    """The run() method must be removed from the Router interface and implementation."""
    router_src = (REPO / "packages/fetch-router/src/lib/router.ts").read_text()
    # The interface had two run() overloads, the implementation had async run<result>
    assert "run<result>(" not in router_src, (
        "run() method signature should be removed from Router"
    )
    assert "async run<result>" not in router_src, (
        "run() implementation should be removed from createRouter()"
    )


# [pr_diff] fail_to_pass
def test_run_tests_removed():
    """The router.run() test suite and its createStorageKey import must be removed."""
    test_src = (REPO / "packages/fetch-router/src/lib/router.test.ts").read_text()
    assert "describe('router.run()'" not in test_src, (
        "router.run() test suite should be removed"
    )
    assert "router.run(" not in test_src, "No router.run() calls should remain in tests"
    assert "createStorageKey" not in test_src, (
        "createStorageKey import (only used by run tests) should be removed"
    )


# [pr_diff] fail_to_pass
def test_change_file_deleted():
    """The unreleased change file for router.run must be deleted."""
    change_file = REPO / "packages/fetch-router/.changes/minor.router-run.md"
    assert not change_file.exists(), "Change file minor.router-run.md should be deleted"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fetch_router_readme_updated():
    """packages/fetch-router/README.md must not document router.run()."""
    readme = (REPO / "packages/fetch-router/README.md").read_text()
    assert "router.run()" not in readme, (
        "README should not document the removed router.run() API"
    )
    assert "Running Code In Request Context" not in readme, (
        "The 'Running Code In Request Context' section should be removed"
    )


# [pr_diff] fail_to_pass
def test_bookstore_readme_updated():
    """demos/bookstore/README.md must not reference router.run()."""
    readme = (REPO / "demos/bookstore/README.md").read_text()
    assert "router.run()" not in readme, (
        "Bookstore demo README should not reference the removed router.run() API"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static / repo_tests) — regression + compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typecheck_passes():
    """TypeScript compilation must pass after the removal."""
    result = subprocess.run(
        ["pnpm", "--filter", "@remix-run/fetch-router", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_remaining_router_tests_pass():
    """The remaining fetch-router tests must still pass."""
    result = subprocess.run(
        [
            "node",
            "--disable-warning=ExperimentalWarning",
            "--test",
            "./packages/fetch-router/src/lib/router.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"
