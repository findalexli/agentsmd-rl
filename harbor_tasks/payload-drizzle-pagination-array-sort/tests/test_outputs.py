#!/usr/bin/env python3
"""
Test harness for payload-drizzle-pagination-array-sort

Verifies the pagination fix for array field sorting by checking:
1. The fix exists in the correct files (fail_to_pass)
2. The repo's CI linter passes (pass_to_pass)
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/payload"

def check_code_has_fix():
    """
    Check that the fix code exists in findMany.ts.

    The fix introduces:
    - oneToManyJoinedTableNames set
    - hasSortOnOneToMany check
    - GROUP BY query with min/max for one-to-many joins

    On base commit (before fix): these don't exist
    After fix: these should be present
    """
    findmany_path = os.path.join(REPO, "packages/drizzle/src/find/findMany.ts")

    with open(findmany_path, 'r') as f:
        content = f.read()

    # Check for distinctive fix patterns
    has_one_to_many = "oneToManyJoinedTableNames" in content
    has_group_by = "groupBy" in content
    has_min_max = "min(column)" in content or "max(column)" in content

    if has_one_to_many and has_group_by and has_min_max:
        print("PASS: Fix code found in findMany.ts")
        return True
    else:
        print(f"FAIL: Fix code missing in findMany.ts")
        print(f"  oneToManyJoinedTableNames: {has_one_to_many}")
        print(f"  groupBy: {has_group_by}")
        print(f"  min/max: {has_min_max}")
        return False


def check_buildquery_has_is_one_to_many():
    """
    Check that buildQuery.ts has isOneToMany in BuildQueryJoinAliases type.
    """
    buildquery_path = os.path.join(REPO, "packages/drizzle/src/queries/buildQuery.ts")

    with open(buildquery_path, 'r') as f:
        content = f.read()

    # Check for isOneToMany in the type definition
    if "isOneToMany" in content:
        print("PASS: isOneToMany found in buildQuery.ts")
        return True
    else:
        print("FAIL: isOneToMany not found in buildQuery.ts")
        return False


def check_addjointable_has_is_one_to_many():
    """
    Check that addJoinTable.ts has isOneToMany parameter.
    """
    addjointable_path = os.path.join(REPO, "packages/drizzle/src/queries/addJoinTable.ts")

    with open(addjointable_path, 'r') as f:
        content = f.read()

    if "isOneToMany" in content:
        print("PASS: isOneToMany found in addJoinTable.ts")
        return True
    else:
        print("FAIL: isOneToMany not found in addJoinTable.ts")
        return False


def check_gettablecolumn_has_is_one_to_many():
    """
    Check that getTableColumnFromPath.ts passes isOneToMany: true for array joins.
    """
    gettable_path = os.path.join(REPO, "packages/drizzle/src/queries/getTableColumnFromPath.ts")

    with open(gettable_path, 'r') as f:
        content = f.read()

    # The fix adds isOneToMany: true when joining array parent tables
    # Look for the pattern where addJoinTable is called with isOneToMany
    if "isOneToMany: true" in content:
        print("PASS: isOneToMany: true found in getTableColumnFromPath.ts")
        return True
    else:
        print("FAIL: isOneToMany: true not found in getTableColumnFromPath.ts")
        return False


# =============================================================================
# PASS_TO_PASS TESTS - repo CI commands that should pass on base commit
# =============================================================================

def test_repo_drizzle_lint():
    """Repo's ESLint passes for the drizzle package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/drizzle",
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_drizzle_lint_target_files():
    """Repo's ESLint passes for the modified source files (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "eslint",
            "src/find/findMany.ts",
            "src/queries/buildQuery.ts",
            "src/queries/addJoinTable.ts",
            "src/queries/getTableColumnFromPath.ts",
        ],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/drizzle",
    )
    assert r.returncode == 0, f"ESLint failed on target files:\n{r.stderr[-500:]}"


def test_repo_typescript_build_drizzle():
    """Drizzle package swc build passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "build:swc"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/drizzle",
    )
    assert r.returncode == 0, f"Drizzle swc build failed:\n{r.stderr[-500:]}"


def test_array_sort_pagination_fix():
    """
    Test that the pagination fix for array field sorting is properly applied.

    The fix modifies 4 files:
    1. packages/drizzle/src/find/findMany.ts - main fix with GROUP BY + min/max
    2. packages/drizzle/src/queries/buildQuery.ts - add isOneToMany to type
    3. packages/drizzle/src/queries/addJoinTable.ts - pass isOneToMany in joins
    4. packages/drizzle/src/queries/getTableColumnFromPath.ts - set isOneToMany: true

    All 4 checks must pass for the fix to be complete.
    """
    checks = [
        check_code_has_fix(),
        check_buildquery_has_is_one_to_many(),
        check_addjointable_has_is_one_to_many(),
        check_gettablecolumn_has_is_one_to_many(),
    ]

    if all(checks):
        print("\nAll fix checks PASSED")
    else:
        print(f"\nFix verification FAILED: {sum(checks)}/4 checks passed")

    # Run pass_to_pass tests (repo CI checks) - these should pass on base commit
    print("\n=== Running pass_to_pass (repo CI) checks ===")
    p2p_results = []
    try:
        test_repo_drizzle_lint()
        print("PASS: test_repo_drizzle_lint")
        p2p_results.append(True)
    except AssertionError as e:
        print(f"FAIL: test_repo_drizzle_lint - {e}")
        p2p_results.append(False)

    try:
        test_repo_drizzle_lint_target_files()
        print("PASS: test_repo_drizzle_lint_target_files")
        p2p_results.append(True)
    except AssertionError as e:
        print(f"FAIL: test_repo_drizzle_lint_target_files - {e}")
        p2p_results.append(False)

    try:
        test_repo_typescript_build_drizzle()
        print("PASS: test_repo_typescript_build_drizzle")
        p2p_results.append(True)
    except AssertionError as e:
        print(f"FAIL: test_repo_typescript_build_drizzle - {e}")
        p2p_results.append(False)

    print(f"\npass_to_pass results: {sum(p2p_results)}/{len(p2p_results)} passed")

    # Overall: fail if fix not present OR if any p2p test failed
    if not all(checks) or not all(p2p_results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    test_array_sort_pagination_fix()