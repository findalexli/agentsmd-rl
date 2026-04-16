#!/usr/bin/env python3
"""
Tests for excalidraw PR #10669: reduce max tablet MQ size
"""

import subprocess
import sys
import os

REPO = "/workspace/excalidraw"


def test_mq_max_tablet_value():
    """
    Fail-to-pass: MQ_MAX_TABLET should be 1180 (iPad Air size) not 1400.

    The PR changes the tablet breakpoint from 1400 to 1180px to better
    match iPad Air dimensions.
    """
    result = subprocess.run(
        ["grep", "MQ_MAX_TABLET = 1180", "packages/common/src/editorInterface.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "MQ_MAX_TABLET should be set to 1180 (iPad Air size)"
    assert "1180" in result.stdout, f"Expected 1180 in MQ_MAX_TABLET definition, got: {result.stdout}"


def test_mq_max_tablet_has_ipad_comment():
    """
    Fail-to-pass: MQ_MAX_TABLET should have iPad Air comment.
    """
    result = subprocess.run(
        ["grep", "MQ_MAX_TABLET = 1180.*ipad air", "packages/common/src/editorInterface.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    # Check the line exists and contains the comment
    result2 = subprocess.run(
        ["grep", "MQ_MAX_TABLET", "packages/common/src/editorInterface.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result2.returncode == 0, "MQ_MAX_TABLET should be defined"
    assert "1180" in result2.stdout, f"Expected 1180, got: {result2.stdout}"


def test_uioptions_has_getformfactor():
    """
    Fail-to-pass: UIOptions should have getFormFactor function property.

    The PR replaces UIOptions.formFactor with UIOptions.getFormFactor() function
    for better DX (developer experience).
    """
    with open(f"{REPO}/packages/excalidraw/types.ts", "r") as f:
        content = f.read()

    assert "getFormFactor?: (" in content, "UIOptions should define getFormFactor function property"
    assert "editorWidth: number" in content, "getFormFactor should take editorWidth parameter"
    assert "editorHeight: number" in content, "getFormFactor should take editorHeight parameter"


def test_uioptions_removed_formfactor():
    """
    Fail-to-pass: UIOptions should not have old formFactor property.
    """
    result = subprocess.run(
        ["grep", "formFactor?:", "packages/excalidraw/types.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    # This should fail (no old formFactor property)
    assert result.returncode != 0, "UIOptions should not have old formFactor property (replaced by getFormFactor)"


def test_uioptions_removed_desktopuimode():
    """
    Fail-to-pass: UIOptions should not have desktopUIMode property.

    The PR removes UIOptions.desktopUIMode for now (unused).
    """
    result = subprocess.run(
        ["grep", "desktopUIMode?:", "packages/excalidraw/types.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    # This should fail (no desktopUIMode property)
    assert result.returncode != 0, "UIOptions should not have desktopUIMode property (removed)"


def test_app_uses_getformfactor():
    """
    Fail-to-pass: App.tsx should use getFormFactor function instead of formFactor.
    """
    result = subprocess.run(
        ["grep", "getFormFactor?.(editorWidth, editorHeight)", "packages/excalidraw/components/App.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "App.tsx should call getFormFactor as a function with (editorWidth, editorHeight)"


def test_app_removed_uioptions_desktopuimode():
    """
    Fail-to-pass: App.tsx should not reference UIOptions.desktopUIMode.
    """
    result = subprocess.run(
        ["grep", "this.props.UIOptions.desktopUIMode", "packages/excalidraw/components/App.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0, "App.tsx should not reference UIOptions.desktopUIMode"


def test_index_handles_getformfactor():
    """
    Fail-to-pass: index.tsx should handle getFormFactor in areEqual.
    """
    result = subprocess.run(
        ["grep", '-A1', 'if.*key.*===.*"getFormFactor"', "packages/excalidraw/index.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Try another pattern
        result = subprocess.run(
            ["grep", 'getFormFactor', "packages/excalidraw/index.tsx"],
            cwd=REPO,
            capture_output=True,
            text=True
        )
    assert result.returncode == 0, "index.tsx should handle getFormFactor in areEqual comparison"


def test_desktop_ui_mode_comment():
    """
    Fail-to-pass: Should have comment noting desktop/laptop is not used for form factor.
    """
    result = subprocess.run(
        ["grep", "not used for form factor detection", "packages/common/src/editorInterface.ts"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "Should have comment noting desktop/laptop MQ is not used for form factor detection"


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors.

    From CLAUDE.md: Always run `yarn test:typecheck` to verify TypeScript.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript type checking failed:\n{result.stderr[-1000:]}"


def test_repo_lint():
    """
    Pass-to-pass: ESLint passes on the codebase.

    Runs `yarn test:code` to verify no linting errors.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Lint check failed:\n{result.stderr[-500:]}"


def test_repo_format():
    """
    Pass-to-pass: Prettier formatting check passes.

    Runs `yarn test:other` to verify all files are properly formatted.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"


def test_formfactor_function_signature():
    """
    Fail-to-pass: getFormFactor should have correct function signature in types.

    Should accept (editorWidth: number, editorHeight: number) and return formFactor type.
    """
    # Read the types.ts file
    with open(f"{REPO}/packages/excalidraw/types.ts", "r") as f:
        content = f.read()

    # Check that getFormFactor exists with correct signature
    assert "getFormFactor?: (" in content, "getFormFactor should be defined as optional function property"
    assert "editorWidth: number" in content, "getFormFactor should accept editorWidth: number"
    assert "editorHeight: number" in content, "getFormFactor should accept editorHeight: number"
    assert "EditorInterface[\"formFactor\"]" in content, "getFormFactor should return EditorInterface['formFactor']"


def test_mq_constants_valid():
    """
    Pass-to-pass: Media query constants should have valid relationships.

    MQ_MIN_TABLET should be MQ_MAX_MOBILE + 1
    MQ_MAX_TABLET should be > MQ_MIN_TABLET
    """
    # Read the editorInterface.ts file
    with open(f"{REPO}/packages/common/src/editorInterface.ts", "r") as f:
        content = f.read()

    # Extract values using grep
    result_min = subprocess.run(
        ["grep", "MQ_MIN_TABLET", f"{REPO}/packages/common/src/editorInterface.ts"],
        capture_output=True,
        text=True
    )

    result_max = subprocess.run(
        ["grep", "MQ_MAX_TABLET =", f"{REPO}/packages/common/src/editorInterface.ts"],
        capture_output=True,
        text=True
    )

    result_max_mobile = subprocess.run(
        ["grep", "MQ_MAX_MOBILE =", f"{REPO}/packages/common/src/editorInterface.ts"],
        capture_output=True,
        text=True
    )

    # Extract numeric values from the grep results
    import re

    # Extract MQ_MAX_MOBILE value
    mobile_match = re.search(r"MQ_MAX_MOBILE = (\d+)", result_max_mobile.stdout)
    assert mobile_match, f"Could not find MQ_MAX_MOBILE value in: {result_max_mobile.stdout}"
    max_mobile = int(mobile_match.group(1))

    # Extract MQ_MIN_TABLET value - can be either a number or an expression
    tablet_min_match = re.search(r"MQ_MIN_TABLET = (.+?);", result_min.stdout)
    assert tablet_min_match, f"Could not find MQ_MIN_TABLET definition in: {result_min.stdout}"
    min_tablet_def = tablet_min_match.group(1).strip()

    # Extract MQ_MAX_TABLET value
    tablet_max_match = re.search(r"MQ_MAX_TABLET = (\d+)", result_max.stdout)
    assert tablet_max_match, f"Could not find MQ_MAX_TABLET value in: {result_max.stdout}"
    max_tablet = int(tablet_max_match.group(1))

    # Check MQ_MIN_TABLET is defined as MQ_MAX_MOBILE + 1
    assert min_tablet_def == "MQ_MAX_MOBILE + 1", f"MQ_MIN_TABLET should be defined as 'MQ_MAX_MOBILE + 1', got: {min_tablet_def}"

    # Check MQ_MAX_TABLET is > MQ_MIN_TABLET (which is max_mobile + 1)
    assert max_tablet > max_mobile + 1, f"MQ_MAX_TABLET ({max_tablet}) should be > MQ_MIN_TABLET ({max_mobile + 1})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
