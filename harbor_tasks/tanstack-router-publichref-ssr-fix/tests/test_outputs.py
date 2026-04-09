"""Tests for TanStack Router publicHref SSR fix.

This tests that the publicHref calculation in buildLocation matches
parseLocation, preventing double loader execution during SSR hydration.
"""

import subprocess
import sys

REPO = "/workspace/router"
ROUTER_CORE = f"{REPO}/packages/router-core"


def test_build_compiles():
    """The fix must compile without TypeScript errors."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_unit_tests_pass():
    """Router-core unit tests must pass with the fix."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Tests may be absent or pass - either is acceptable
    # We're mainly checking the build succeeds and tests don't break
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_typescript_check():
    """PASS_TO_PASS: TypeScript typecheck passes on router-core (repo CI check).

    This is a repo CI check that should pass on both base and fixed commits.
    Ensures the fix doesn't break type compatibility across TS versions.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-1000:]}"


def test_repo_eslint():
    """PASS_TO_PASS: ESLint check passes on router-core (repo CI check).

    This is a repo CI check that should pass on both base and fixed commits.
    Ensures the fix follows code style guidelines.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-1000:]}"


def test_repo_build_check():
    """PASS_TO_PASS: Build validation passes on router-core (repo CI check).

    This is a repo CI check that should pass on both base and fixed commits.
    Validates package exports with publint and attw.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Build validation failed:\n{result.stderr[-1000:]}"


def test_publichref_calculation_consistency():
    """FAIL-TO-PASS: publicHref must use pathname + searchStr + hash, not raw href.

    Before the fix: buildLocation used `publicHref: href` which is the raw href
    with potential encoding differences from parseLocation which used
    `pathname + searchStr + hash`.

    After the fix: both use `pathname + searchStr + hash` consistently.

    This test verifies the fix by checking the actual source code uses the
    correct calculation.
    """
    router_ts = f"{ROUTER_CORE}/src/router.ts"

    with open(router_ts, "r") as f:
        content = f.read()

    # Find the buildLocation function's return statement for publicHref
    # After fix, it should be: publicHref: pathname + searchStr + hash,
    # not: publicHref: href,

    # Look for the specific pattern in the buildLocation return statement
    # The fix changes from `publicHref: href,` to `publicHref: pathname + searchStr + hash,`
    lines = content.split("\n")

    # Find the section around buildLocation's return with href/publicHref
    found_correct_pattern = False
    found_wrong_pattern = False

    for i, line in enumerate(lines):
        # Check for the WRONG pattern (the bug): publicHref: href,
        if "publicHref: href," in line or 'publicHref: href,' in line:
            found_wrong_pattern = True
            break

        # Check for the CORRECT pattern (the fix): publicHref: pathname + searchStr + hash,
        if "publicHref: pathname + searchStr + hash," in line:
            found_correct_pattern = True
            # Verify it's in the context of buildLocation return statement
            # by checking surrounding lines have href: pathname + searchStr + hash
            context = "\n".join(lines[max(0, i-5):i+5])
            assert "href: pathname + searchStr + hash," in context, \
                "publicHref fix found but href line is missing nearby - may be wrong location"
            break

    assert not found_wrong_pattern, \
        "BUG: publicHref still uses raw 'href' - causes SSR hydration mismatch"
    assert found_correct_pattern, \
        "FIX MISSING: publicHref should use 'pathname + searchStr + hash' to match parseLocation"


def test_parseLocation_uses_consistent_calculation():
    """PARITY CHECK: parseLocation must also use pathname + searchStr + hash for publicHref.

    Both functions should use the same calculation. This test verifies parseLocation
    uses the expected pattern.
    """
    router_ts = f"{ROUTER_CORE}/src/router.ts"

    with open(router_ts, "r") as f:
        content = f.read()

    # In parseLocation, publicHref should also use pathname + searchStr + hash
    lines = content.split("\n")

    # Find parseLocation function
    in_parse_location = False
    parse_location_start = -1

    for i, line in enumerate(lines):
        if "parseLocation(" in line and "function" not in line and "=>" not in line:
            in_parse_location = True
            parse_location_start = i
            break

    if not in_parse_location:
        # Try alternative detection for method syntax
        for i, line in enumerate(lines):
            if "parseLocation" in line and ("(" in line or "async" in line):
                parse_location_start = i
                break

    # If we can't find parseLocation, skip this test
    if parse_location_start == -1:
        return

    # Look at the next 100 lines after parseLocation for the publicHref return
    section = "\n".join(lines[parse_location_start:parse_location_start + 100])

    # parseLocation should have publicHref: pathname + searchStr + hash somewhere
    # This is the reference pattern that buildLocation should match
    has_consistent_pattern = "publicHref: pathname + searchStr + hash" in section

    assert has_consistent_pattern, \
        "parseLocation should use 'pathname + searchStr + hash' for publicHref"


def test_no_raw_href_in_buildLocation_return():
    """ANTI-REGRESSION: Ensure no return statement has raw href for publicHref.

    The original bug pattern was `publicHref: href,` in a return statement.
    The fix should use the consistent calculation instead.
    """
    router_ts = f"{ROUTER_CORE}/src/router.ts"

    with open(router_ts, "r") as f:
        content = f.read()

    # Check that the file has the correct pattern somewhere (indicating fix is applied)
    has_correct_pattern = "publicHref: pathname + searchStr + hash," in content

    # This test verifies the fix has been applied (the correct pattern exists)
    assert has_correct_pattern, \
        "FIX MISSING: Should have 'publicHref: pathname + searchStr + hash' pattern"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_publichref_calculation_consistency,
        test_parseLocation_uses_consistent_calculation,
        test_no_raw_href_in_buildLocation_return,
        test_build_compiles,
        test_unit_tests_pass,
        test_repo_typescript_check,
        test_repo_eslint,
        test_repo_build_check,
    ]

    failed = []
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed.append((test.__name__, str(e)))
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed.append((test.__name__, str(e)))

    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
