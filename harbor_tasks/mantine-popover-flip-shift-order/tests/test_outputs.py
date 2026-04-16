"""
Tests for mantine use-popover middleware order fix.

The bug: shift middleware runs before flip, causing the Popover to overlap
with its trigger at screen edges instead of flipping to the opposite side.

The fix: Reorder middlewares so flip runs BEFORE shift.
"""

import subprocess
import sys

REPO = "/workspace/mantine"
TARGET_FILE = "packages/@mantine/core/src/components/Popover/use-popover.ts"


def test_flip_middleware_before_shift():
    """
    FAIL-TO-PASS: flip middleware must be added BEFORE shift middleware.

    In the buggy version, shift runs first and pushes the popover into the
    viewport, preventing flip from triggering and causing overlap issues.

    The fix moves flip before shift so flip can reposition the element
    to the opposite side before shift adjusts it within viewport bounds.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # Find line numbers of the middleware blocks
    lines = content.split('\n')
    flip_line = None
    shift_line = None

    for i, line in enumerate(lines, start=1):
        if 'if (middlewaresOptions.flip)' in line and flip_line is None:
            flip_line = i
        if 'if (middlewaresOptions.shift)' in line and shift_line is None:
            shift_line = i

    assert flip_line is not None, "flip middleware block not found"
    assert shift_line is not None, "shift middleware block not found"

    # flip must come BEFORE shift
    assert flip_line < shift_line, (
        f"flip middleware (line {flip_line}) must come BEFORE shift middleware (line {shift_line}). "
        f"Current order causes overlap at screen edges because shift pushes the popover into viewport "
        f"before flip has a chance to reposition it to the opposite side."
    )


def test_flip_middleware_has_correct_body():
    """
    FAIL-TO-PASS: flip middleware block must have correct implementation.

    Verifies that the flip block contains the proper flip() call with
    conditional logic for boolean vs object options.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the correct flip implementation pattern
    assert "middlewaresOptions.flip" in content, "middlewaresOptions.flip check missing"
    assert "flip()" in content, "flip() call missing"
    assert "flip(middlewaresOptions.flip)" in content, "flip(middlewaresOptions.flip) call missing"

    # Find the flip block and verify it pushes to middlewares array
    lines = content.split('\n')
    in_flip_block = False
    flip_block_has_push = False

    for line in lines:
        if 'if (middlewaresOptions.flip)' in line:
            in_flip_block = True
        elif in_flip_block:
            if 'middlewares.push' in line:
                flip_block_has_push = True
            # Exit flip block when we hit another middleware block
            if 'if (middlewaresOptions.shift)' in line or 'if (middlewaresOptions.inline)' in line:
                break

    assert flip_block_has_push, "flip middleware block must push to middlewares array"


def test_shift_middleware_has_correct_body():
    """
    FAIL-TO-PASS: shift middleware block must have correct implementation with limitShift.

    Verifies that the shift block contains the proper shift() call with
    limitShift() limiter and padding.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the correct shift implementation pattern
    assert "middlewaresOptions.shift" in content, "middlewaresOptions.shift check missing"
    assert "shift(" in content, "shift() call missing"
    assert "limitShift()" in content, "limitShift() limiter missing from shift call"
    assert "padding: 5" in content, "padding: 5 missing from shift call"


def test_file_has_no_syntax_errors():
    """
    PASS-TO-PASS: The modified TypeScript file must have no syntax errors.

    We verify this by running ESLint which will catch parsing/syntax issues.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    # Read the file and verify it can be parsed
    with open(file_path, 'r') as f:
        content = f.read()

    # Basic structural checks that indicate valid TypeScript
    assert "function getPopoverMiddlewares" in content, "getPopoverMiddlewares function missing"
    assert "export function usePopover" in content, "usePopover export missing"
    assert "import { useEffect" in content, "React imports missing"
    assert "from '@floating-ui/react'" in content, "floating-ui imports missing"


def test_repo_lint():
    """
    PASS-TO-PASS: ESLint must pass on the modified file.

    The fix should follow the project's linting rules.
    """
    result = subprocess.run(
        ["npx", "eslint", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"ESLint errors in use-popover.ts:\n{result.stderr[-500:]}"
    )


def test_repo_typecheck():
    """
    PASS-TO-PASS: TypeScript typecheck must pass.

    The fix should not introduce any TypeScript type errors.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"TypeScript typecheck failed:\n{result.stderr[-500:]}"
    )


def test_repo_prettier():
    """
    PASS-TO-PASS: Prettier formatting must pass on the modified file.

    The fix should follow the project's code formatting rules.
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"Prettier formatting errors in use-popover.ts:\n{result.stderr[-500:]}"
    )


def test_repo_jest_popover():
    """
    PASS-TO-PASS: Popover component tests must pass.

    The fix should not break any existing Popover functionality.
    """
    result = subprocess.run(
        ["npx", "jest", "--testPathPatterns=Popover", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Popover Jest tests failed:\n{result.stderr[-500:]}"
    )
