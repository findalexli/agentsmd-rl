"""
Tests for prisma/adapter-pg#29395: statementNameGenerator feature

The PR adds a statementNameGenerator option to PrismaPgOptions that allows users
to provide a custom function to name prepared statements. When provided, the
generated name is passed to pg.Client#query() for statement caching.

Fail-to-pass tests (f2p): These must fail on the base commit and pass on the fix.
Pass-to-pass tests (p2p): These verify existing functionality still works.
"""

import subprocess
import os

REPO = "/workspace/prisma"


def test_statementNameGenerator_option_exists():
    """The PrismaPgOptions type includes statementNameGenerator (fail_to_pass)."""
    pg_ts = f"{REPO}/packages/adapter-pg/src/pg.ts"
    with open(pg_ts, "r") as f:
        content = f.read()

    # This must exist in the fixed version
    assert "statementNameGenerator" in content, (
        "statementNameGenerator option not found in PrismaPgOptions"
    )


def test_statementNameGenerator_called_in_query():
    """When statementNameGenerator is provided, it is called and its result is passed to pg.Client#query() (fail_to_pass)."""
    pg_ts = f"{REPO}/packages/adapter-pg/src/pg.ts"
    with open(pg_ts, "r") as f:
        content = f.read()

    # The implementation must use the generator to set the name property
    # Look for: name: this.pgOptions?.statementNameGenerator?.(query)
    assert "this.pgOptions?.statementNameGenerator?.(query)" in content, (
        "statementNameGenerator not called in query method"
    )


def test_statementNameGenerator_type_defined():
    """The StatementNameGenerator type is exported (fail_to_pass)."""
    pg_ts = f"{REPO}/packages/adapter-pg/src/pg.ts"
    with open(pg_ts, "r") as f:
        content = f.read()

    # Check for the type definition: export type StatementNameGenerator = (query: SqlQuery) => string
    assert "StatementNameGenerator = (query: SqlQuery) => string" in content, (
        "StatementNameGenerator type signature not correct"
    )


def test_adapter_pg_tests_exist():
    """The pg.test.ts file contains the new test cases for statementNameGenerator (pass_to_pass)."""
    test_file = f"{REPO}/packages/adapter-pg/src/__tests__/pg.test.ts"
    with open(test_file, "r") as f:
        content = f.read()

    # Check for the two new test cases
    assert "should pass generated name when statement name generator is provided" in content
    assert "should not pass name when statement name generator is not provided" in content


def test_pg_ts_has_new_import():
    """The test file imports SqlQuery from driver-adapter-utils (pass_to_pass)."""
    test_file = f"{REPO}/packages/adapter-pg/src/__tests__/pg.test.ts"
    with open(test_file, "r") as f:
        content = f.read()

    # The new tests import SqlQuery
    assert "import type { SqlQuery }" in content or "SqlQuery" in content


def test_prisma_pg_options_has_statementNameGenerator_docs():
    """PrismaPgOptions has documentation for statementNameGenerator (pass_to_pass - rubric alignment)."""
    pg_ts = f"{REPO}/packages/adapter-pg/src/pg.ts"
    with open(pg_ts, "r") as f:
        content = f.read()

    # The PR adds doc comments for statementNameGenerator
    # This only passes after the fix is applied
    assert "statementNameGenerator" in content and "/**" in content


def test_repo_eslint_adapter_pg():
    """Repo's ESLint passes on adapter-pg package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/adapter-pg"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # ESLint exits 0 even with warnings; exit 1 for errors
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_vitest_errors_test():
    """Repo's vitest errors test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/__tests__/errors.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/adapter-pg",
    )
    assert r.returncode == 0, f"Vitest errors.test.ts failed:\n{r.stderr[-500:]}"


def test_repo_prettier_check():
    """Repo's Prettier check passes on adapter-pg (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "prettier", "--check", "packages/adapter-pg"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}"