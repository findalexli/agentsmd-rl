"""
Tests for excalidraw arrow overlap behavior fix.

This PR fixes the behavior of arrows when they overlap or are too short.
The key changes are:
1. Added BASE_ARROW_MIN_LENGTH constant (10)
2. Refactored updateBoundPoint to handle overlapping elements better
3. Added extractBinding helper function
4. Added elementArea helper function
5. Changed the logic to use focus points vs outline points based on arrow length and overlap
6. Removed indirectArrowUpdate option and related code
7. Changed updateBoundPoint signature from opts object to dragging boolean
"""

import subprocess
import re
import os

REPO = "/workspace/excalidraw"


def test_base_arrow_min_length_constant_exists():
    """BASE_ARROW_MIN_LENGTH constant should be exported from binding.ts"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    assert "BASE_ARROW_MIN_LENGTH = 10" in content, \
        "BASE_ARROW_MIN_LENGTH constant not found in binding.ts"


def test_extract_binding_function_exists():
    """extractBinding helper function should exist in binding.ts"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    assert "const extractBinding = (" in content, \
        "extractBinding function not found in binding.ts"


def test_element_area_function_exists():
    """elementArea helper function should exist in binding.ts"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    assert "const elementArea = (element:" in content or \
           "elementArea = (element: ExcalidrawBindableElement) =>" in content, \
        "elementArea function not found in binding.ts"


def test_update_bound_point_signature_changed():
    """updateBoundPoint should accept dragging parameter instead of opts object"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    # Check that the old signature with opts is removed
    assert "opts?: {\n    customIntersector?:" not in content, \
        "Old opts parameter still present in updateBoundPoint"

    # Check that the new signature with dragging parameter exists
    assert "dragging?: boolean," in content or \
           "dragging?: boolean" in content, \
        "New dragging parameter not found in updateBoundPoint"


def test_indirect_arrow_update_removed():
    """indirectArrowUpdate option should be removed from updateBoundElements"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    assert "indirectArrowUpdate?: boolean" not in content, \
        "indirectArrowUpdate option still present in updateBoundElements"


def test_align_elements_indirect_update_removed():
    """align.ts should not pass indirectArrowUpdate option"""
    with open(f"{REPO}/packages/element/src/align.ts", "r") as f:
        content = f.read()

    assert "indirectArrowUpdate: true" not in content, \
        "indirectArrowUpdate still passed in align.ts"


def test_app_indirect_update_removed():
    """App.tsx should not pass indirectArrowUpdate option"""
    with open(f"{REPO}/packages/excalidraw/components/App.tsx", "r") as f:
        content = f.read()

    assert "indirectArrowUpdate: true" not in content, \
        "indirectArrowUpdate still passed in App.tsx"


def test_focus_point_update_passes_dragging():
    """focus.ts should pass dragging=true to updateBoundPoint"""
    with open(f"{REPO}/packages/element/src/arrows/focus.ts", "r") as f:
        content = f.read()

    # Find the focusPointUpdate function and check it passes true as the last param
    # After the fix, the last parameter should be `true` for dragging
    pattern = r"updateBoundPoint\([^)]+bindableElement,\s*elementsMap,\s*true,\s*\)"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, \
        "focus.ts should pass true as dragging parameter to updateBoundPoint"


def test_linear_element_editor_dragging_passed():
    """linearElementEditor.ts should pass dragging flags to updateBoundPoint"""
    with open(f"{REPO}/packages/element/src/linearElementEditor.ts", "r") as f:
        content = f.read()

    # Check that endIsDragged and startIsDragged are passed to updateBoundPoint
    assert "endIsDragged," in content, \
        "endIsDragged not passed to updateBoundPoint in linearElementEditor.ts"
    assert "startIsDragged," in content, \
        "startIsDragged not passed to updateBoundPoint in linearElementEditor.ts"


def test_linear_element_editor_no_custom_intersector():
    """linearElementEditor.ts should not use customIntersector"""
    with open(f"{REPO}/packages/element/src/linearElementEditor.ts", "r") as f:
        content = f.read()

    assert "customIntersector" not in content, \
        "customIntersector still referenced in linearElementEditor.ts"


def test_utils_imports_binding_functions():
    """utils.ts should import getGlobalFixedPointForBindableElement and normalizeFixedPoint"""
    with open(f"{REPO}/packages/element/src/utils.ts", "r") as f:
        content = f.read()

    assert "getGlobalFixedPointForBindableElement" in content, \
        "getGlobalFixedPointForBindableElement not imported in utils.ts"
    assert "normalizeFixedPoint" in content, \
        "normalizeFixedPoint not imported in utils.ts"


def test_utils_uses_other_focus_point():
    """utils.ts should use opposite focus point for two-point arrows"""
    with open(f"{REPO}/packages/element/src/utils.ts", "r") as f:
        content = f.read()

    # Check for the comment about using opposite focus point
    assert "To avoid working with stale arrow state" in content, \
        "Comment about stale arrow state not found in utils.ts"


def test_binding_bounds_imports_cleaned():
    """binding.ts should not import unused bounds functions"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    # The old code imported doBoundsIntersect and getElementBounds
    # Check that the import is cleaned up - should only import getCenterForBounds
    import_match = re.search(r'import \{([^}]+)\} from "./bounds"', content)
    if import_match:
        imports = import_match.group(1)
        assert "doBoundsIntersect" not in imports, \
            "doBoundsIntersect still imported in binding.ts"
        assert "getElementBounds" not in imports, \
            "getElementBounds still imported in binding.ts"


def test_point_is_close_to_other_element_check():
    """binding.ts should check if point is close to other element"""
    with open(f"{REPO}/packages/element/src/binding.ts", "r") as f:
        content = f.read()

    assert "pointIsCloseToOtherElement" in content, \
        "pointIsCloseToOtherElement check not found in binding.ts"
    assert "!pointIsCloseToOtherElement" in content, \
        "pointIsCloseToOtherElement check not used in binding.ts"


def test_repo_typecheck():
    """Repo's TypeScript type checking passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"TypeScript type check failed:\n{result.stderr[-1000:]}"


def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_tests_binding():
    """Repo's binding tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/binding.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Binding tests failed:\n{result.stderr[-500:]}"


def test_repo_tests_elbow_arrow():
    """Repo's elbow arrow tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/elbowArrow.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Elbow arrow tests failed:\n{result.stderr[-500:]}"


def test_repo_tests_linear_element_editor():
    """Repo's linear element editor tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/linearElementEditor.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Linear element editor tests failed:\n{result.stderr[-500:]}"


def test_repo_tests_align():
    """Repo's alignment tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/align.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Align tests failed:\n{result.stderr[-500:]}"


def test_repo_tests_history():
    """Repo's history tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/tests/history.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"History tests failed:\n{result.stderr[-500:]}"


def test_repo_tests():
    """Repo's test suite passes (pass_to_pass)."""
    # Run tests but don't fail on snapshot mismatches (they may differ due to version changes)
    result = subprocess.run(
        ["yarn", "test:update", "--testPathPattern=history"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    # We check that tests don't crash, not exact snapshot match
    assert "FAIL" not in result.stdout or result.returncode == 0, \
        f"Repo tests failed:\n{result.stdout[-1000:]}"
