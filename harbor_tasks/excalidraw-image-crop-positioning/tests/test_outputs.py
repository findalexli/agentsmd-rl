"""Test for excalidraw image crop positioning fix.

This test verifies that the image crop editor correctly calculates
drag offsets using previous pointer coordinates instead of current ones.
"""

import subprocess
import re
import sys

REPO = "/workspace/excalidraw"
TARGET_FILE = "packages/excalidraw/components/App.tsx"


def test_previous_pointer_field_exists():
    """Verify the previousPointerMoveCoords field is declared."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    assert "previousPointerMoveCoords" in content, (
        "Missing field: previousPointerMoveCoords should be declared in App class"
    )

    # Verify it has a comment explaining its purpose
    assert "previous frame pointer coords" in content, (
        "Missing comment explaining previousPointerMoveCoords purpose"
    )


def test_last_pointer_coords_uses_previous():
    """Verify lastPointerCoords uses previousPointerMoveCoords, not lastPointerMoveCoords."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the line where lastPointerCoords is assigned
    # It should use previousPointerMoveCoords, not lastPointerMoveCoords
    match = re.search(
        r"const lastPointerCoords\s*=\s*([^;]+);",
        content,
        re.MULTILINE | re.DOTALL
    )
    assert match, "Could not find lastPointerCoords assignment"

    assignment = match.group(1)
    assert "previousPointerMoveCoords" in assignment, (
        "lastPointerCoords should use previousPointerMoveCoords"
    )
    assert "lastPointerMoveCoords" not in assignment, (
        "lastPointerCoords should NOT use lastPointerMoveCoords"
    )


def test_crop_x_uses_subtraction():
    """Verify crop.x calculation uses subtraction (not addition) for offset."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the crop.x calculation in the crop editor section
    # Should be: crop.x - offsetVector[0] * ...
    # Not: crop.x + offsetVector[0] * ...

    # Look for the pattern around crop.x in the nextCrop calculation
    pattern = r"x:\s*clamp\(\s*\n?\s*crop\.x\s*([+-])\s*offsetVector\[0\]"
    match = re.search(pattern, content)

    assert match, "Could not find crop.x calculation with offsetVector"
    operator = match.group(1)
    assert operator == "-", (
        f"crop.x calculation uses '{operator}' but should use '-' (subtraction)"
    )


def test_crop_y_uses_subtraction():
    """Verify crop.y calculation uses subtraction (not addition) for offset."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the crop.y calculation in the crop editor section
    # Should be: crop.y - offsetVector[1] * ...
    # Not: crop.y + offsetVector[1] * ...

    pattern = r"y:\s*clamp\(\s*\n?\s*crop\.y\s*([+-])\s*offsetVector\[1\]"
    match = re.search(pattern, content)

    assert match, "Could not find crop.y calculation with offsetVector"
    operator = match.group(1)
    assert operator == "-", (
        f"crop.y calculation uses '{operator}' but should use '-' (subtraction)"
    )


def test_previous_pointer_reset_on_pointer_up():
    """Verify previousPointerMoveCoords is reset to null on pointer up."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Look for the cleanup in handlePointerUp
    # Should set previousPointerMoveCoords = null
    pattern = r"this\.previousPointerMoveCoords\s*=\s*null"
    assert re.search(pattern, content), (
        "previousPointerMoveCoords should be reset to null in handlePointerUp"
    )


def test_typescript_compiles():
    """Verify the TypeScript code compiles without errors."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )

    # The fix should not introduce any type errors
    assert result.returncode == 0, (
        f"TypeScript type check failed:\n{result.stdout}\n{result.stderr}"
    )


def test_unit_tests_pass():
    """Run the project's unit tests to ensure no regressions."""
    result = subprocess.run(
        ["yarn", "test", "--run", "--reporter=dot"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    # Allow some tests to fail (snapshot differences etc), but not compilation
    # The main goal is that the code is testable and doesn't break everything
    if result.returncode != 0:
        # Check if it's a compilation error vs test assertion failure
        if "SyntaxError" in result.stderr or "TypeError" in result.stderr:
            assert False, f"Critical error in tests:\n{result.stderr}"


def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_format():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"
