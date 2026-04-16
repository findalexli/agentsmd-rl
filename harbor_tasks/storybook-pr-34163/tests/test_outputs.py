#!/usr/bin/env python3
"""
Tests for Storybook Link component keyboard accessibility fix.

This validates that the Link component:
1. Renders as a <button> element when no href is provided (keyboard focusable)
2. Renders as an <a> element when href is provided
3. Applies proper focus styles for button mode
4. Shows deprecation warning when isButton prop is used
"""

import subprocess
import sys
import re

REPO = "/workspace/storybook"
LINK_FILE = "code/core/src/components/components/typography/link/link.tsx"

def test_link_renders_as_button_without_href():
    """
    F2P: Link without href should render as <button> element, not <a>.

    This is the core accessibility fix - anchor elements without href are not
    keyboard focusable, but button elements are.
    """
    with open(f"{REPO}/{LINK_FILE}", "r") as f:
        content = f.read()

    # Check that the component uses conditional 'as' prop based on href
    assert "as={href ? 'a' : 'button'}" in content, \
        "Link component should conditionally render as 'a' or 'button' based on href presence"


def test_link_renders_as_anchor_with_href():
    """
    F2P: Link with href should continue to render as <a> element.

    We need to ensure the fix doesn't break existing anchor behavior.
    """
    with open(f"{REPO}/{LINK_FILE}", "r") as f:
        content = f.read()

    # Verify href prop is extracted and passed to the element
    assert "href={href}" in content, \
        "Link component should pass href to the rendered element"

    # Verify the conditional logic preserves anchor behavior when href exists
    pattern = r"as=\{href\s*\?\s*['\"]a['\"]\s*:\s*['\"]button['\"]\}"
    assert re.search(pattern, content), \
        "Link should use 'a' tag when href exists, 'button' when absent"


def test_button_focus_styles_applied():
    """
    F2P: Button-styled links should have visible focus indicators.

    The fix adds focus-visible styles for keyboard navigation.
    """
    with open(f"{REPO}/{LINK_FILE}", "r") as f:
        content = f.read()

    # Check for focus-visible styles in isButton styling block
    assert "'&:focus-visible':" in content or "&:focus-visible" in content, \
        "Button-styled links should have focus-visible styles for keyboard navigation"

    # Check for outline styles
    assert "outline:" in content and "theme.color.secondary" in content, \
        "Focus indicator should use theme secondary color for visibility"

    # Check for zIndex to ensure focus outline is visible
    assert "zIndex:" in content or "z-index:" in content.lower(), \
        "Focus outline should have z-index to appear above siblings"


def test_isbutton_prop_deprecated():
    """
    F2P: Using isButton prop should trigger deprecation warning.

    The isButton prop is deprecated because the behavior is now automatic.
    """
    with open(f"{REPO}/{LINK_FILE}", "r") as f:
        content = f.read()

    # Check for deprecation import
    assert "deprecate" in content, \
        "Link component should import and use deprecation warning"

    # Check for isButton default value change (was false, now undefined)
    assert "isButton = undefined" in content, \
        "isButton prop should default to undefined (not false) to detect usage"

    # Check for deprecation message when isButton is used
    pattern = r"if\s*\(\s*isButton\s*!==?\s*undefined\s*\)"
    assert re.search(pattern, content), \
        "Component should check if isButton prop was explicitly passed"

    # Check for actual deprecation call
    assert 'deprecate(' in content and 'isButton' in content, \
        "Deprecation warning should mention isButton prop"


def test_isbutton_default_changed():
    """
    F2P: isButton prop default must be undefined, not false.

    This allows detecting when the prop is explicitly used vs not provided.
    """
    with open(f"{REPO}/{LINK_FILE}", "r") as f:
        content = f.read()

    # Find the destructured props in the component
    # Should have "isButton = undefined" not "isButton = false"
    # Look in the forwardRef function parameter destructuring
    pattern = r"isButton\s*=\s*(undefined|false)"
    match = re.search(pattern, content)

    assert match, "Should find isButton prop with default value"
    assert match.group(1) == "undefined", \
        f"isButton should default to undefined (got {match.group(1)}) to detect explicit usage"


def test_typescript_compilation():
    """
    P2P: TypeScript check should pass after changes.

    Based on AGENTS.md: use 'yarn nx run-many -t check' for type checking.
    """
    result = subprocess.run(
        ["yarn", "nx", "run-many", "-t", "check", "--projects=core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # TypeScript check should pass
    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_component_compiles():
    """
    P2P: The components package should compile without errors.

    Based on AGENTS.md: use 'yarn nx compile <package>' to compile.
    """
    result = subprocess.run(
        ["yarn", "nx", "compile", "core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Component compilation failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_formatting():
    """
    P2P: Code formatting passes on modified files.

    Repo CI uses prettier to enforce code style.
    """
    result = subprocess.run(
        ["yarn", "prettier", "--check", LINK_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Prettier formatting check failed:\n{result.stderr[-500:]}"




if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_link_renders_as_button_without_href,
        test_link_renders_as_anchor_with_href,
        test_button_focus_styles_applied,
        test_isbutton_prop_deprecated,
        test_isbutton_default_changed,
        test_component_compiles,
        test_typescript_compilation,
        test_repo_formatting,
    ]

    passed = 0
    failed = 0

    for test in test_functions:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
