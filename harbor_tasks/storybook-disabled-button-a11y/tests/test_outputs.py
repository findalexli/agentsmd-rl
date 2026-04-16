"""Test outputs for Storybook disabled button accessibility fix.

This module validates that the Button component correctly implements
keyboard accessibility for disabled buttons by using aria-disabled instead
of the native disabled attribute.
"""

import subprocess
import sys
import os

REPO = "/workspace/storybook"
BUTTON_FILE = f"{REPO}/code/core/src/components/components/Button/Button.tsx"

def _run_in_repo(cmd, timeout=300, cwd=None):
    """Run a command in the repo directory."""
    workdir = cwd or REPO
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=workdir,
        shell=isinstance(cmd, str)
    )
    return result


def test_button_uses_aria_disabled():
    """Disabled buttons use aria-disabled instead of disabled attribute (f2p).

    The fix changes from the native 'disabled' attribute to 'aria-disabled' so that
    disabled buttons remain keyboard-focusable for accessibility.
    """
    with open(BUTTON_FILE, 'r') as f:
        content = f.read()

    # Should use aria-disabled attribute
    assert "aria-disabled={disabled || readOnly ? 'true' : undefined}" in content, \
        "Button should use aria-disabled attribute"

    # Should NOT use the native disabled prop on StyledButton (now uses $disabled)
    lines = content.split('\n')
    for line in lines:
        # Check for the old pattern: disabled={disabled || readOnly}
        # (must NOT be $disabled - that's the new transient prop)
        idx = line.find('disabled={disabled || readOnly}')
        if idx != -1 and idx > 0 and line[idx - 1] != '$':
            assert False, f"Button still uses native disabled prop: {line}"


def test_disabled_button_click_handler_blocked():
    """Disabled buttons don't trigger click handlers (f2p).

    When disabled or readOnly, the onClick handler should be undefined
    to prevent click interactions.
    """
    with open(BUTTON_FILE, 'r') as f:
        content = f.read()

    # Should conditionally set onClick based on disabled state
    assert "onClick={disabled || readOnly ? undefined : handleClick}" in content, \
        "Button should block click handlers when disabled"


def test_styled_button_uses_transient_disabled_prop():
    """StyledButton uses transient $disabled prop (f2p).

    The styled component should use the transient $disabled prop
    (with $ prefix) to avoid passing it to the DOM.
    """
    with open(BUTTON_FILE, 'r') as f:
        content = f.read()

    # Should define the prop as $disabled in the interface
    assert '$disabled?: boolean;' in content, \
        "StyledButton should use $disabled prop (transient)"


def test_styled_button_uses_disabled_prop_for_styling():
    """StyledButton styling uses $disabled prop correctly (f2p).

    The component styling should reference $disabled for visual
    disabled state (cursor, opacity).
    """
    with open(BUTTON_FILE, 'r') as f:
        content = f.read()

    # Check for the styling logic using $disabled
    # cursor: readOnly ? 'inherit' : $disabled ? 'not-allowed' : 'pointer'
    assert "cursor: readOnly ? 'inherit' : $disabled ? 'not-allowed' : 'pointer'" in content, \
        "StyledButton should use $disabled for cursor styling"

    # opacity: $disabled && !readOnly ? 0.5 : 1
    assert "opacity: $disabled && !readOnly ? 0.5 : 1" in content, \
        "StyledButton should use $disabled for opacity styling"


def test_repo_typecheck():
    """Repo TypeScript checking passes (pass_to_pass).

    Based on AGENTS.md: Use 'yarn nx run-many -t check' for TypeScript checking.
    """
    result = _run_in_repo(
        ["yarn", "nx", "run-many", "-t", "check", "--projects=storybook,@storybook/core"],
        timeout=300
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_button_compiles():
    """Button component compiles successfully (pass_to_pass).

    The Button component and its dependencies should compile without errors.
    """
    result = _run_in_repo(
        ["yarn", "nx", "compile", "core"],
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_prettier_check():
    """Repo code formatting passes (pass_to_pass).

    The Button component and repo code should follow prettier formatting rules.
    """
    result = _run_in_repo(
        ["yarn", "prettier", "--check", "code/core/src/components/components/Button/Button.tsx"],
        timeout=60
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_core_check_package():
    """Core package type checking passes (pass_to_pass).

    Runs the repo's check-package script for type checking the core package.
    """
    result = _run_in_repo(
        ["yarn", "exec", "jiti", "./scripts/check/check-package.ts", "--cwd", "code/core"],
        timeout=120
    )
    assert result.returncode == 0, f"Core type check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_core_build_package():
    """Core package builds successfully (pass_to_pass).

    Runs the repo's build-package script to verify core package compiles.
    """
    result = _run_in_repo(
        ["yarn", "exec", "jiti", "./scripts/build/build-package.ts", "--cwd", "code/core"],
        timeout=300
    )
    assert result.returncode == 0, f"Core build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
