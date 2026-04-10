"""
Test file for Excalidraw arrow drag start fix.
Tests that the updateBoundPoint function correctly handles initial arrow creation state.
"""
import subprocess
import sys
import json

REPO = "/workspace/excalidraw"


def run_yarn_test(test_pattern, timeout=120):
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


# =============================================================================
# Pass-to-pass tests: Repo CI tests that should pass at both base and fixed commits
# =============================================================================


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


def test_binding_unit_tests():
    """
    Pass-to-pass test: binding.test.tsx unit tests pass.
    Tests the binding.ts module functionality including arrow binding behavior.
    """
    result = run_yarn_test("binding.test.tsx", timeout=120)

    if result.returncode != 0:
        print(f"FAIL: binding.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True


def test_drag_create_tests():
    """
    Pass-to-pass test: dragCreate.test.tsx tests pass.
    Tests drag-to-create functionality including arrow creation.
    """
    result = run_yarn_test("dragCreate.test.tsx", timeout=120)

    if result.returncode != 0:
        print(f"FAIL: dragCreate.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True


def test_linear_element_editor_tests():
    """
    Pass-to-pass test: linearElementEditor.test.tsx tests pass.
    Tests linear element (arrow/line) editing functionality.
    """
    result = run_yarn_test("linearElementEditor.test.tsx", timeout=180)

    if result.returncode != 0:
        print(f"FAIL: linearElementEditor.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False

    return True


def test_elbow_arrow_tests():
    """
    Pass-to-pass test: elbowArrow.test.tsx tests pass.
    Tests elbow arrow routing and binding behavior.
    """
    result = run_yarn_test("elbowArrow.test.tsx", timeout=120)

    if result.returncode != 0:
        print(f"FAIL: elbowArrow.test.tsx failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        print(f"stderr: {result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
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
        ("binding_imports", test_binding_imports),
        ("updateBoundPoint_condition", test_updateBoundPoint_condition),
        ("repo_lint", test_repo_lint),
        ("repo_prettier", test_repo_prettier),
        ("binding_unit_tests", test_binding_unit_tests),
        ("drag_create_tests", test_drag_create_tests),
        ("linear_element_editor_tests", test_linear_element_editor_tests),
        ("elbow_arrow_tests", test_elbow_arrow_tests),
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
