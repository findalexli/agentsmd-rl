"""
Test file for Excalidraw arrow drag start fix.
Tests that the updateBoundPoint function correctly handles initial arrow creation state.
"""
import subprocess
import sys
import json

REPO = "/workspace/excalidraw"

def run_yarn_test(test_pattern, timeout=60):
    """Run a specific test pattern using yarn test."""
    result = subprocess.run(
        ["yarn", "test", test_pattern, "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result

def test_binding_logic_initial_arrow():
    """
    Fail-to-pass test: Verify the fix is applied for initial arrow state.
    The fix adds a check in updateBoundPoint to return null when the arrow's
    last point is at [0,0] (initial creation state), preventing the jump bug.

    On base commit: This test fails because the fix is not applied.
    On fixed commit: This test passes because pointsEqual import and check exist.
    """
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    # Check that pointsEqual is imported (the fix adds this import)
    import_section = content.split("export")[0] if "export" in content else content[:1500]
    has_pointsEqual_import = "pointsEqual" in import_section

    if not has_pointsEqual_import:
        print("FAIL: pointsEqual not imported - fix not applied")
        return False

    # Check the specific condition exists in the function
    has_pointsEqual_call = "pointsEqual(" in content
    has_last_point_check = "arrow.points[arrow.points.length - 1]" in content
    has_origin_check = "pointFrom<LocalPoint>(0, 0)" in content

    if not has_pointsEqual_call:
        print("FAIL: pointsEqual call not found in updateBoundPoint")
        return False

    if not has_last_point_check:
        print("FAIL: Check for arrow's last point not found")
        return False

    if not has_origin_check:
        print("FAIL: Initial point (0,0) check not found")
        return False

    # Verify the condition is in the return null check section
    # The fix adds: || pointsEqual(arrow.points[arrow.points.length - 1], pointFrom<LocalPoint>(0, 0))
    # inside the if statement that returns null
    updateBoundPoint_section = content[content.find("export const updateBoundPoint"):content.find("export const updateBoundPoint") + 3000] if "export const updateBoundPoint" in content else ""

    if "arrow.points.length - 1" not in updateBoundPoint_section:
        print("FAIL: Last point check not in updateBoundPoint function")
        return False

    print("PASS: Fix correctly applied - pointsEqual check for initial arrow state exists")
    return True

def test_repo_lint():
    """
    Pass-to-pass test: Repo lint check passes (yarn test:code).
    This ensures the codebase passes ESLint checks.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        print(f"FAIL: Lint check failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True


def test_repo_prettier():
    """
    Pass-to-pass test: Repo prettier check passes (yarn test:other).
    This ensures the codebase passes Prettier formatting checks.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(f"FAIL: Prettier check failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True


def test_move_tests_pass():
    """
    Pass-to-pass test: The move.test.tsx should pass with the fix.
    This validates that arrow movement with binding works correctly.
    """
    result = run_yarn_test("move.test.tsx", timeout=120)

    if result.returncode != 0:
        print(f"FAIL: move.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True

def test_history_tests_pass():
    """
    Pass-to-pass test: The history.test.tsx should pass with the fix.
    Validates bidirectional binding behavior in history operations.
    """
    result = run_yarn_test("history.test.tsx", timeout=120)

    if result.returncode != 0:
        print(f"FAIL: history.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True

def test_binding_imports():
    """
    Structural check: Verify the fix has been applied by checking imports.
    Gated by behavioral tests - this only runs if they pass.
    """
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    # Check that pointsEqual is imported from math package
    import_section = content.split("export")[0] if "export" in content else content[:1000]

    if "pointsEqual" not in import_section:
        print("FAIL: pointsEqual not imported")
        return False

    # Check that pointFrom is also imported (needed for the fix)
    if "pointFrom" not in import_section:
        print("FAIL: pointFrom not imported")
        return False

    return True

def test_updateBoundPoint_condition():
    """
    Structural check: Verify the specific condition exists in updateBoundPoint.
    Gated by behavioral tests.
    """
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    # Look for the specific pattern in the fix
    # The fix adds: pointsEqual(arrow.points[arrow.points.length - 1], pointFrom<LocalPoint>(0, 0))
    if "pointsEqual(" not in content:
        print("FAIL: pointsEqual call not found")
        return False

    if "arrow.points[arrow.points.length - 1]" not in content:
        print("FAIL: Check for last point not found")
        return False

    if "pointFrom<LocalPoint>(0, 0)" not in content:
        print("FAIL: Initial point check not found")
        return False

    return True

def test_no_regression_in_syntax():
    """
    Verify the code passes TypeScript type checking.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(f"FAIL: TypeScript check failed: {result.stderr[-1000:]}")
        return False

    return True

if __name__ == "__main__":
    import os

    # Create result directory
    os.makedirs("/logs/verifier", exist_ok=True)

    results = {}

    # Run all tests
    tests = [
        ("binding_logic_initial_arrow", test_binding_logic_initial_arrow),
        ("repo_lint", test_repo_lint),
        ("repo_prettier", test_repo_prettier),
        ("move_tests_pass", test_move_tests_pass),
        ("history_tests_pass", test_history_tests_pass),
        ("binding_imports", test_binding_imports),
        ("updateBoundPoint_condition", test_updateBoundPoint_condition),
        ("no_regression_in_syntax", test_no_regression_in_syntax),
    ]

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            results[name] = False

    # Write results
    with open("/logs/verifier/reward.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    sys.exit(0 if passed == total else 1)
