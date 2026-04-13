"""
Tests for Excalidraw angle-lock binding fix.

This test suite verifies that when dragging linear element endpoints with
the Shift key held (angle lock), the angle is constrained to discrete angles
even when the endpoint is being bound to another element.
"""

import subprocess
import json
import sys
from pathlib import Path

REPO = Path("/workspace/excalidraw")


def run_typecheck():
    """Run TypeScript type checking."""
    # Use npx yarn since yarn may not be in PATH
    result = subprocess.run(
        ["npx", "yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def run_binding_tests():
    """Run the binding-related tests from the repo's test suite."""
    result = subprocess.run(
        ["yarn", "test", "packages/element/tests/binding.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def test_angle_locked_param_exists_in_binding():
    """
    Test that the angleLocked parameter exists in binding.ts function signatures.

    This is a fail-to-pass test: the base code doesn't have angleLocked,
    the fix adds it.
    """
    binding_file = REPO / "packages/element/src/binding.ts"
    content = binding_file.read_text()

    # Check that angleLocked is in the opts parameter of key functions
    # These are the structural changes that enable the behavioral fix
    assert "angleLocked?: boolean;" in content, (
        "angleLocked parameter not found in binding.ts opts type"
    )

    # Check it's used in getBindingStrategyForDraggingBindingElementEndpoints
    assert "opts?: {\n    newArrow?: boolean;\n    angleLocked?: boolean;" in content or \
           "angleLocked?: boolean;" in content, (
        "angleLocked not in getBindingStrategyForDraggingBindingElementEndpoints opts"
    )


def test_angle_locked_used_in_strategy_logic():
    """
    Test that angleLocked is actually used in the binding strategy logic.

    The fix adds logic to use angleLocked when determining if we should
    use 'orbit' mode for the other endpoint.
    """
    binding_file = REPO / "packages/element/src/binding.ts"
    content = binding_file.read_text()

    # Look for the specific pattern where angleLocked is used to determine orbit mode
    # This is the key behavioral change
    assert "opts?.angleLocked && otherBindableElement" in content, (
        "angleLocked not used in binding strategy logic"
    )


def test_shift_key_check_simplified_in_linear_editor():
    """
    Test that the over-restrictive shift key checks are removed.

    The bug was that the code checked:
      shouldRotateWithDiscreteAngle(event) && !hoveredElement && !element.startBinding && !element.endBinding

    This prevented angle locking when binding was active.

    The fix simplifies this to just:
      shouldRotateWithDiscreteAngle(event)
    """
    editor_file = REPO / "packages/element/src/linearElementEditor.ts"
    content = editor_file.read_text()

    # Check that the old restrictive pattern is NOT present
    # The old pattern had checks for binding status combined with angle check
    bad_pattern = "shouldRotateWithDiscreteAngle(event) &&\n      !hoveredElement &&\n      !element.startBinding &&\n      !element.endBinding"

    assert bad_pattern not in content, (
        "Old restrictive angle-lock check still present in linearElementEditor.ts"
    )


def test_point_dragging_updates_passes_angle_locked():
    """
    Test that pointDraggingUpdates receives angleLocked instead of shiftKey.

    The function signature changed from shiftKey to angleLocked, and
    the logic now passes shouldRotateWithDiscreteAngle() result instead
    of raw shiftKey.
    """
    editor_file = REPO / "packages/element/src/linearElementEditor.ts"
    content = editor_file.read_text()

    # Check that pointDraggingUpdates receives angleLocked parameter
    assert "angleLocked: boolean," in content or "angleLocked: boolean" in content, (
        "pointDraggingUpdates doesn't have angleLocked parameter"
    )

    # Check that shouldRotateWithDiscreteAngle is passed instead of shiftKey
    # The parameter is passed positionally, so check for the function call pattern
    assert "shouldRotateWithDiscreteAngle(event)," in content or \
           "shouldRotateWithDiscreteAngle(event) && singlePointDragged" in content, (
        "shouldRotateWithDiscreteAngle result not passed as angleLocked"
    )


def test_action_finalize_passes_angle_locked():
    """
    Test that actionFinalize passes angleLocked to bindOrUnbindBindingElement.
    """
    action_file = REPO / "packages/excalidraw/actions/actionFinalize.tsx"
    content = action_file.read_text()

    # Check for angleLocked being passed
    assert "angleLocked: shouldRotateWithDiscreteAngle(event)" in content, (
        "actionFinalize doesn't pass angleLocked to bindOrUnbindBindingElement"
    )


def test_app_component_passes_angle_locked():
    """
    Test that App.tsx passes angleLocked when creating new arrows.
    """
    app_file = REPO / "packages/excalidraw/components/App.tsx"
    content = app_file.read_text()

    # Check for angleLocked being passed in initial binding
    assert "angleLocked: shouldRotateWithDiscreteAngle(event.nativeEvent)" in content, (
        "App.tsx doesn't pass angleLocked for new arrow binding"
    )


def test_typescript_compiles():
    """
    Test that the TypeScript code compiles without errors.

    This catches type mismatches from the parameter changes.
    """
    result = run_typecheck()
    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_binding_strategy_respects_angle_lock():
    """
    Integration test: verify binding strategy logic structure.

    This test verifies that the fixed code structure allows angle-locked
    binding to work correctly by checking the key code paths exist.
    """
    binding_file = REPO / "packages/element/src/binding.ts"
    content = binding_file.read_text()

    # The fix adds a code path that handles angleLocked for the 'other' endpoint
    # when one endpoint is being dragged with angle lock enabled

    # 1. Check that otherEndpoint is computed (needed for the fix)
    assert "LinearElementEditor.getPointAtIndexGlobalCoordinates(" in content, (
        "otherEndpoint computation not found - needed for angle-locked binding"
    )

    # 2. Check that projectFixedPointOntoDiagonal is called in the angleLocked path
    assert "projectFixedPointOntoDiagonal(" in content, (
        "projectFixedPointOntoDiagonal not used in binding logic"
    )

    # 3. Verify the ternary structure with angleLocked exists
    # The fix adds: : opts?.angleLocked && otherBindableElement ? { mode: "orbit", ... }
    lines = content.split('\n')
    angle_locked_ternary_found = False
    for i, line in enumerate(lines):
        if "opts?.angleLocked && otherBindableElement" in line:
            # Check following lines have the orbit mode assignment
            following = ''.join(lines[i:i+10])
            if 'mode: "orbit"' in following:
                angle_locked_ternary_found = True
                break

    assert angle_locked_ternary_found, (
        "angleLocked conditional path with orbit mode not found"
    )


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and fix
# =============================================================================


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_binding_tests():
    """Repo's binding tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "packages/element/tests/binding.test.tsx", "--watch=false"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Binding tests failed:\n{r.stderr[-500:]}"


def test_repo_linear_element_editor_tests():
    """Repo's linear element editor tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "packages/element/tests/linearElementEditor.test.tsx", "--watch=false"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Linear element editor tests failed:\\n{r.stderr[-500:]}"


def test_repo_elbow_arrow_tests():
    """Repo's elbow arrow tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "packages/element/tests/elbowArrow.test.tsx", "--watch=false"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Elbow arrow tests failed:\\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
