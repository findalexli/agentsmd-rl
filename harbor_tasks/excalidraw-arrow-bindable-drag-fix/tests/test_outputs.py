"""
Test suite for excalidraw PR #10676:
Fix: Arrow drag start in bindable area jumps across bindable

The bug: When starting to drag an arrow from within a bindable element's area,
the arrow's points were being incorrectly updated, causing the arrow to "jump"
across the bindable element instead of starting from the proper position.

The fix: Add a check in updateBoundPoint() to detect when an arrow is in its
initial state (last point equals [0,0]) and skip point updates in that case.
"""

import subprocess
import sys
import json

REPO = "/workspace/excalidraw"

def test_updateBoundPoint_initial_arrow_check_exists():
    """
    Fail-to-pass: Verify the fix for initial arrow state check exists in binding.ts.

    The fix adds a condition to check if the arrow is in its initial state
    (last point equals [0,0]) before updating bound points. This prevents
    the arrow from jumping when dragging starts within a bindable area.
    """
    binding_file = f"{REPO}/packages/element/src/binding.ts"

    with open(binding_file, 'r') as f:
        content = f.read()

    # Check for the key parts of the fix
    assert "pointsEqual" in content, "pointsEqual import not found"
    assert "Initial arrow created on pointer down needs to not update the points" in content, \
        "Fix comment not found - the initial arrow check is missing"

    # Check that the pointsEqual call exists with the right pattern
    assert "arrow.points[arrow.points.length - 1]" in content, \
        "Arrow points length check not found"
    assert "pointFrom<LocalPoint>(0, 0)" in content, \
        "Zero point check not found"

def test_updateBoundPoint_returns_null_for_initial_arrow():
    """
    Fail-to-pass: Verify the logic returns null for initial arrow state.

    When an arrow is in its initial state (created on pointer down with
    the last point at [0,0]), updateBoundPoint should return null to
    prevent unwanted point updates that cause the jumping behavior.
    """
    binding_file = f"{REPO}/packages/element/src/binding.ts"

    with open(binding_file, 'r') as f:
        content = f.read()

    # Find the updateBoundPoint function and check the early return condition
    # The fix adds: || pointsEqual(arrow.points[arrow.points.length - 1], pointFrom<LocalPoint>(0, 0))
    # to the existing condition that returns null

    # The condition should be part of an if statement that returns null
    import re

    # Look for the pattern where pointsEqual is used to check initial arrow state
    # The fix checks if last point equals [0,0] which indicates initial arrow state
    # The actual code has the pointsEqual call on its own line with the args on subsequent lines
    pattern = r'pointsEqual\s*\(\s*\n?\s*arrow\.points\[\s*arrow\.points\.length\s+-\s+1\s*\]\s*,\s*\n?\s*pointFrom<LocalPoint>\s*\(\s*0\s*,\s*0\s*\)\s*,?\s*\n?\s*\)'

    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, \
        "The initial arrow check (pointsEqual with arrow.points[length-1] and [0,0]) not found"

    # Also verify the check is part of a condition that leads to returning null
    # Find the updateBoundPoint function and check its structure
    func_start = content.find("export const updateBoundPoint")
    func_content = content[func_start:func_start + 3000]

    # The pointsEqual check should be in a condition that returns null
    assert "return null" in func_content, \
        "return null not found in updateBoundPoint function"

    # Verify the pointsEqual check is in the early return condition (before the main logic)
    # by checking it appears before the first 'return null'
    pointsEqual_pos = func_content.find("pointsEqual")
    return_null_pos = func_content.find("return null")
    assert pointsEqual_pos < return_null_pos, \
        "pointsEqual check should come before return null in updateBoundPoint"

def test_repo_typecheck():
    """
    Pass-to-pass: Verify the TypeScript code compiles without errors.

    Runs the repo's typecheck command (yarn test:typecheck / tsc) to ensure
    the fix doesn't break TypeScript compilation.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Note: tsc might fail due to pre-existing issues, but we check the specific error
    # related to our changes isn't present
    if result.returncode != 0:
        # Check that our specific changes don't cause new errors
        stderr = result.stderr.lower() if result.stderr else ""
        stdout = result.stdout.lower() if result.stdout else ""
        combined = stderr + stdout

        # The fix should not introduce binding.ts errors
        assert "binding.ts" not in combined or "pointsEqual" not in combined, \
            f"TypeScript compilation failed with binding.ts error: {result.stderr or result.stdout}"


def test_repo_lint():
    """
    Pass-to-pass: Verify the code passes ESLint checks.

    Runs the repo's lint command (yarn test:code / eslint) to ensure
    the fix follows the codebase's style guidelines.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_prettier():
    """
    Pass-to-pass: Verify the code passes Prettier formatting checks.

    Runs the repo's prettier check (yarn test:other / prettier --list-different)
    to ensure the fix follows the codebase's formatting guidelines.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_flip_tests():
    """
    Pass-to-pass: Run the repository's flip element tests.

    The flip.test.tsx tests element flipping functionality including
    bound text and arrows. Verifies core transformation logic still works.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/tests/flip.test.tsx", "--no-watch"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Flip tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_regression_tests():
    """
    Pass-to-pass: Run the repository's regression tests.

    The regressionTests.test.tsx contains tests for fixed bugs and
    edge cases. Ensures the fix doesn't reintroduce old issues.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/tests/regressionTests.test.tsx", "--no-watch"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Regression tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_dragcreate_tests():
    """
    Pass-to-pass: Run the repository's drag creation tests.

    The dragCreate.test.tsx tests arrow and element creation via dragging,
    which is directly related to the fix for arrow drag behavior.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/tests/dragCreate.test.tsx", "--no-watch"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Drag creation tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_clipboard_tests():
    """
    Pass-to-pass: Run the repository's clipboard tests.

    The clipboard.test.tsx tests copy/paste functionality which involves
    element serialization and deserialization. Verifies core utilities work.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/tests/clipboard.test.tsx", "--no-watch"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Clipboard tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"

def test_pointsEqual_function_imported():
    """
    Fail-to-pass: Verify that pointsEqual is properly imported from the math module.

    The fix relies on the pointsEqual utility function which must be imported
    from the math module for the comparison to work correctly.
    """
    binding_file = f"{REPO}/packages/element/src/binding.ts"

    with open(binding_file, 'r') as f:
        content = f.read()

    # Check that pointsEqual is imported from @excalidraw/math
    # Look for the specific import pattern
    import re

    # Match the import block from @excalidraw/math and check it contains pointsEqual
    pattern = r'import\s*\{[^}]*pointsEqual[^}]*\}\s*from\s*["\']@excalidraw/math["\']'
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, \
        "pointsEqual not found in imports from @excalidraw/math in binding.ts"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_install_and_test():
    """pass_to_pass | CI scoped vitest run: binding + drag create tests"""
    r = subprocess.run(
        ["bash", "-lc",
         "yarn test:app run packages/element/tests/binding.test.tsx"
         " packages/excalidraw/tests/dragCreate.test.tsx"],
        cwd=REPO,
        capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, (
        f"CI scoped test run failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
