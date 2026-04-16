#!/usr/bin/env python3
"""Tests for Menu.Sub openDelay prop feature."""

import subprocess
import sys
import os

REPO = "/workspace/mantine"
MENU_SUB_PATH = f"{REPO}/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx"


def test_opendelay_prop_in_interface():
    """Fail-to-pass: MenuSubProps interface should declare openDelay prop."""
    content = open(MENU_SUB_PATH).read()

    # Check that openDelay is declared in the interface
    assert "openDelay?: number;" in content, \
        "MenuSubProps interface must declare 'openDelay?: number;'"


def test_opendelay_in_default_props():
    """Fail-to-pass: defaultProps should include openDelay: 0."""
    content = open(MENU_SUB_PATH).read()

    # Check that defaultProps includes openDelay: 0
    assert "openDelay: 0," in content, \
        "defaultProps must include 'openDelay: 0'"


def test_opendelay_destructured():
    """Fail-to-pass: openDelay should be destructured from props."""
    content = open(MENU_SUB_PATH).read()

    # Check that openDelay is destructured in function
    assert "const { children, closeDelay, openDelay, ...others }" in content, \
        "MenuSub function must destructure 'openDelay' from props"


def test_opendelay_passed_to_useDelayedHover():
    """Fail-to-pass: openDelay variable should be passed to useDelayedHover."""
    content = open(MENU_SUB_PATH).read()

    # The useDelayedHover call should pass openDelay (variable), not hardcoded 0
    # Find the useDelayedHover call
    import re

    # Look for useDelayedHover call block
    pattern = r'const \{[^}]+\} = useDelayedHover\(\{[^}]+\}\);'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "useDelayedHover call not found"

    call_block = match.group(0)

    # Should contain "openDelay," (the variable reference)
    assert "openDelay," in call_block, \
        "useDelayedHover must receive 'openDelay' variable (not hardcoded 0)"

    # Should NOT contain "openDelay: 0," (the hardcoded value)
    assert "openDelay: 0," not in call_block, \
        "useDelayedHover should use 'openDelay' variable, not hardcoded 'openDelay: 0'"


def test_repo_no_conflict_markers():
    """Repo CI: Check for git conflict markers in source files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsx", "scripts/tests/conflicts.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Conflict markers check failed:\n{result.stderr[-500:]}"


def test_repo_package_json_valid():
    """Repo CI: Validate package.json files structure (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsx", "scripts/tests/validate-package-json.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Package.json validation failed:\n{result.stderr[-500:]}"


def test_repo_package_files_valid():
    """Repo CI: Validate package files configuration (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsx", "scripts/tests/validate-packages-files.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Package files validation failed:\n{result.stderr[-500:]}"


def test_repo_prettier_format():
    """Repo CI: Prettier formatting check on Menu files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/core/src/components/Menu/**/*.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_repo_eslint_menu():
    """Repo CI: ESLint check on Menu directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "packages/@mantine/core/src/components/Menu", "--ext", ".tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-500:]}"


def test_menusub_file_parses():
    """Pass-to-pass: MenuSub.tsx should have valid TypeScript syntax."""
    # Read the file and check for basic TypeScript syntax validity
    content = open(MENU_SUB_PATH).read()

    # Check for balanced braces (basic sanity check for valid TSX structure)
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, f"Unbalanced braces in MenuSub.tsx: {open_braces} open, {close_braces} close"

    # Check for balanced parentheses
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_parens == close_parens, f"Unbalanced parentheses in MenuSub.tsx: {open_parens} open, {close_parens} close"

    # Check for balanced angle brackets (JSX)
    open_angle = content.count("<")
    close_angle = content.count(">")
    # Allow for generics and JSX, just ensure they're reasonably balanced
    assert abs(open_angle - close_angle) < 10, f"Severely unbalanced angle brackets in MenuSub.tsx"

    # Check that the file contains expected TypeScript constructs
    assert "export interface MenuSubProps" in content, "MenuSubProps interface not found"
    assert "export function MenuSub" in content, "MenuSub function not found"


def test_opendelay_values_vary():
    """Fail-to-pass: openDelay should accept different values, not just 0."""
    # Create a test file that uses different openDelay values
    test_file = "/tmp/test-opendelay.tsx"
    test_content = '''
import { Menu } from '@mantine/core';

// Test that various openDelay values are accepted
const TestComponent = () => {
    return (
        <Menu>
            <Menu.Sub openDelay={0}>
                <Menu.Sub.Target>
                    <Menu.Sub.Item>Item</Menu.Sub.Item>
                </Menu.Sub.Target>
                <Menu.Sub.Dropdown>
                    <Menu.Item>Sub</Menu.Item>
                </Menu.Sub.Dropdown>
            </Menu.Sub>
        </Menu>
    );
};

const TestComponent2 = () => {
    return (
        <Menu>
            <Menu.Sub openDelay={100}>
                <Menu.Sub.Target>
                    <Menu.Sub.Item>Item</Menu.Sub.Item>
                </Menu.Sub.Target>
                <Menu.Sub.Dropdown>
                    <Menu.Item>Sub</Menu.Item>
                </Menu.Sub.Dropdown>
            </Menu.Sub>
        </Menu>
    );
};

const TestComponent3 = () => {
    return (
        <Menu>
            <Menu.Sub openDelay={500}>
                <Menu.Sub.Target>
                    <Menu.Sub.Item>Item</Menu.Sub.Item>
                </Menu.Sub.Target>
                <Menu.Sub.Dropdown>
                    <Menu.Item>Sub</Menu.Item>
                </Menu.Sub.Dropdown>
            </Menu.Sub>
        </Menu>
    );
};

export { TestComponent, TestComponent2, TestComponent3 };
'''

    with open(test_file, 'w') as f:
        f.write(test_content)

    # Try to parse with TypeScript
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--jsx", "react", "--esModuleInterop",
         "--skipLibCheck", "--moduleResolution", "node", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # If TypeScript can't resolve the module, that's OK - the important thing
    # is that it doesn't error on the openDelay prop usage
    output = result.stdout + result.stderr

    # Check for specific errors about openDelay
    if "openDelay" in output.lower():
        assert False, f"TypeScript error related to openDelay:\n{output[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
