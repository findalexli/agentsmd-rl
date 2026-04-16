#!/usr/bin/env python3
"""
Test suite for excalidraw arrow binding fix.

This tests that when dragging one end of an arrow, the other end's "fixed" (inside)
binding is not incorrectly converted to "orbit" binding.
"""

import subprocess
import sys
import os

# Repository path
REPO = "/workspace/excalidraw"


def test_binding_ts_never_override_check_exists():
    """
    F2P: Verify the otherNeverOverride check exists in binding.ts

    The fix adds a check to prevent converting fixed bindings to orbit when
the other endpoint has an inside (fixed) binding.
    """
    binding_file = os.path.join(REPO, "packages/element/src/binding.ts")
    with open(binding_file, "r") as f:
        content = f.read()

    # Check for the key parts of the fix
    assert "otherNeverOverride" in content, "Missing otherNeverOverride variable"
    assert "arrowStartIsInside" in content, "Missing arrowStartIsInside reference"


def test_app_ts_tracks_arrow_start_is_inside():
    """
    F2P: Verify App.tsx tracks arrowStartIsInside in initialState

    The fix requires tracking whether the arrow started with an inside binding
    so that the binding logic can avoid overriding it.
    """
    app_file = os.path.join(REPO, "packages/excalidraw/components/App.tsx")
    with open(app_file, "r") as f:
        content = f.read()

    # Check for the arrowStartIsInside tracking
    assert "arrowStartIsInside: event.altKey" in content, \
        "Missing arrowStartIsInside tracking in App.tsx"


def test_binding_logic_preserves_inside_binding():
    """
    F2P: Verify binding.ts logic preserves inside bindings

    When otherBinding?.mode === "inside", the otherNeverOverride flag should be
    set to true, preventing the binding from being converted to orbit.
    """
    binding_file = os.path.join(REPO, "packages/element/src/binding.ts")
    with open(binding_file, "r") as f:
        content = f.read()

    # Check the logic: otherBinding?.mode === "inside" determines never override
    assert 'otherBinding?.mode === "inside"' in content, \
        "Missing check for existing inside binding mode"

    # Check that the never override logic gates the orbit conversion
    lines = content.split("\n")
    found_other_never_override = False
    found_gated_logic = False

    for i, line in enumerate(lines):
        if "otherNeverOverride" in line and "opts?.newArrow" in line:
            found_other_never_override = True
        # After the fix, the other: BindingStrategy should be gated by !otherNeverOverride
        if "const other: BindingStrategy = !otherNeverOverride" in line:
            found_gated_logic = True

    assert found_other_never_override, "Missing otherNeverOverride calculation"
    assert found_gated_logic, "Missing gated logic for other BindingStrategy"


def test_repo_typecheck():
    """
    P2P: TypeScript compilation passes (repo CI).

    Runs yarn test:typecheck to verify the code compiles without TypeScript errors.
    From lint.yml workflow.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_lint():
    """
    P2P: ESLint passes (repo CI).

    Runs yarn test:code to verify linting passes. From lint.yml workflow.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Lint check failed:\n{result.stderr[-500:]}"


def test_repo_prettier():
    """
    P2P: Prettier formatting passes (repo CI).

    Runs yarn test:other to verify code formatting. From lint.yml workflow.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_repo_binding_tests():
    """
    P2P: Binding-specific unit tests pass (repo CI).

    Runs binding.test.tsx which tests the arrow binding functionality
    modified by this PR. From test.yml workflow.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/element/tests/binding.test.tsx", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Binding tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_element_tests():
    """
    P2P: Element package unit tests pass (repo CI).

    Runs all element package tests to ensure no regressions in the
    packages/element module.
    """
    result = subprocess.run(
        ["yarn", "test:app", "packages/element/tests/", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Element tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_no_orbit_override_for_fixed_binding():
    """
    F2P: Structural test - the fix must gate the orbit mode assignment

    Without the fix, the code unconditionally assigns mode: "orbit" when
    altFocusPoint exists. With the fix, this is gated by !otherNeverOverride.
    """
    binding_file = os.path.join(REPO, "packages/element/src/binding.ts")
    with open(binding_file, "r") as f:
        content = f.read()

    # Find the section where the fix should be
    # Before fix: directly checks altFocusPoint and returns orbit mode
    # After fix: checks !otherNeverOverride first

    # Verify the fix structure: the mode: "orbit" block should be inside a
    # conditional that's gated by !otherNeverOverride

    # Look for pattern where mode: "orbit" is nested under !otherNeverOverride condition
    lines = content.split("\n")
    in_other_binding_strategy = False
    found_never_override_guard = False

    for i, line in enumerate(lines):
        if "const other: BindingStrategy = !otherNeverOverride" in line:
            found_never_override_guard = True
            # Check the next several lines contain the orbit mode assignment
            subsequent_lines = "\n".join(lines[i:i+30])
            assert 'mode: "orbit"' in subsequent_lines, \
                "orbit mode should be in the gated section"
            break

    assert found_never_override_guard, \
        "Missing the otherNeverOverride guard in other BindingStrategy"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
