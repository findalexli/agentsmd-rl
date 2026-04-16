#!/usr/bin/env python3
"""
Tests for superset PR #38960: Live CSS preview in PropertiesModal

Key behaviors to verify:
1. handleCustomCssChange exists and implements debounced dispatch
2. handleOnCancel clears timers and restores original CSS
3. Timer cleanup on component unmount
4. Original CSS is captured on modal open
5. TypeScript types are correct (no 'any' types in new code)
6. Redux actions are properly dispatched
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/superset"
FRONTEND = f"{REPO}/superset-frontend"
TARGET_FILE = f"{FRONTEND}/src/dashboard/components/PropertiesModal/index.tsx"


def test_original_css_ref_exists():
    """Fail-to-pass: originalCss ref must exist to store original CSS."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for originalCss ref declaration
    assert "const originalCss = useRef<string | null>(null)" in content, \
        "Missing originalCss ref with proper type"
    assert "const cssDebounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)" in content, \
        "Missing cssDebounceTimer ref with proper type"


def test_handle_custom_css_change_exists():
    """Fail-to-pass: handleCustomCssChange callback must exist with debounce logic."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the handler function
    assert "const handleCustomCssChange = useCallback" in content, \
        "Missing handleCustomCssChange useCallback"

    # Check for debounce timer management
    assert "cssDebounceTimer.current = setTimeout" in content, \
        "Missing setTimeout for debounce"
    assert "500" in content, \
        "Missing 500ms debounce delay"

    # Check for dispatch of dashboardInfoChanged with CSS
    assert 'dispatch(dashboardInfoChanged({ css }))' in content or \
           'dispatch(dashboardInfoChanged({css}))' in content, \
        "Missing dispatch of dashboardInfoChanged with CSS"


def test_cancel_handler_restores_css():
    """Fail-to-pass: handleOnCancel must restore original CSS and clear timers."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that handleOnCancel exists and has the right logic
    # Look for the function definition
    cancel_pattern = r'const handleOnCancel = \(\) => \{'
    match = re.search(cancel_pattern, content)
    assert match, "handleOnCancel should be defined as a function body, not arrow to onHide"

    # Check for timer clearing
    assert "cssDebounceTimer.current" in content and "clearTimeout" in content, \
        "Missing timer cleanup in cancel handler"

    # Check for original CSS restoration
    assert "originalCss.current" in content, \
        "Missing reference to originalCss in cancel handler"

    # Check for dispatch of original CSS
    assert "dispatch(dashboardInfoChanged({ css: originalCss.current }))" in content or \
           'dispatch(dashboardInfoChanged({css: originalCss.current}))' in content, \
        "Missing dispatch to restore original CSS on cancel"


def test_unmount_cleanup_exists():
    """Fail-to-pass: useEffect cleanup must clear debounce timer on unmount."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the cleanup useEffect - should have an empty deps array and cleanup function
    # This is the pattern: useEffect(() => () => { cleanup }, [])
    cleanup_pattern = r'useEffect\(\s*\(\)\s*=>\s*\(\)\s*=>\s*\{[^}]*cssDebounceTimer\.current[^}]*\}'
    assert re.search(cleanup_pattern, content, re.DOTALL), \
        "Missing useEffect cleanup to clear debounce timer on unmount"


def test_original_css_capture_on_open():
    """Fail-to-pass: Original CSS must be captured when modal opens."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the effect that resets originalCss when show becomes true
    assert "originalCss.current = null" in content, \
        "Missing logic to reset originalCss reference when modal opens"

    # Check for null check before capturing original CSS
    assert "if (originalCss.current === null)" in content, \
        "Missing null check to prevent overwriting original CSS"


def test_dashboard_info_changed_imported():
    """Fail-to-pass: dashboardInfoChanged action must be imported."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for import
    assert "import { dashboardInfoChanged } from 'src/dashboard/actions/dashboardInfo'" in content or \
           'import {dashboardInfoChanged} from "src/dashboard/actions/dashboardInfo"' in content or \
           "dashboardInfoChanged" in content, \
        "Missing dashboardInfoChanged import or usage"


def test_no_explicit_any_types():
    """Fail-to-pass: New code should not use explicit 'any' types (per AGENTS.md)."""
    with open(TARGET_FILE, 'r') as f:
        lines = content = f.read()

    # Find the new code sections by looking for the refs and handlers
    # The refs should use proper types, not 'any'
    bad_patterns = [
        "useRef<any>",
        "useRef<any[]>",
    ]

    for pattern in bad_patterns:
        assert pattern not in content, \
            f"Found forbidden 'any' type pattern: {pattern}"


def test_props_use_handler_not_setter():
    """Fail-to-pass: onCustomCssChange prop should use handler, not direct setter."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the prop usage - should use handleCustomCssChange, not setCustomCss
    # This checks that the child component receives the debounced handler
    assert "onCustomCssChange={handleCustomCssChange}" in content, \
        "onCustomCssChange prop should use handleCustomCssChange, not setCustomCss"

    # Make sure setCustomCss is still used internally but not passed to child
    assert "setCustomCss(css)" in content or "setCustomCss(css)" in content.replace(" ", ""), \
        "setCustomCss should still be called within handleCustomCssChange"


def test_repo_jest_tests_pass():
    """Pass-to-pass: Existing PropertiesModal Jest tests should pass."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "PropertiesModal.test.tsx", "--watchAll=false", "--passWithNoTests"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    # Allow it to pass with no tests found (in case file naming is different)
    # but fail on actual test failures
    assert result.returncode == 0, \
        f"PropertiesModal tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_lint_full_passes():
    """Pass-to-pass: Full lint (oxlint + custom rules) passes on the repo."""
    result = subprocess.run(
        ["npm", "run", "lint:full"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Lint full failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_custom_rules_pass():
    """Pass-to-pass: Superset custom rules check passes."""
    result = subprocess.run(
        ["npm", "run", "check:custom-rules"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Custom rules check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_dashboard_actions_tests_pass():
    """Pass-to-pass: Dashboard actions tests pass (covering dashboardInfoChanged and related actions)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "src/dashboard/actions/", "--watchAll=false", "--passWithNoTests", "--maxWorkers=2"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Dashboard actions tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_typescript_compiles():
    """Pass-to-pass: TypeScript should compile without errors in target file."""
    # Run the repo's typecheck command (from package.json scripts)
    result = subprocess.run(
        ["npm", "run", "type"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for type errors specifically in our target file
    output = result.stdout + result.stderr
    target_file_errors = [
        line for line in output.split('\n')
        if 'PropertiesModal/index.tsx' in line and 'error TS' in line
    ]

    assert not target_file_errors, \
        f"TypeScript errors in PropertiesModal/index.tsx:\n{chr(10).join(target_file_errors[-10:])}"


def test_eslint_no_errors():
    """Pass-to-pass: ESLint should pass on the target file."""
    result = subprocess.run(
        ["npm", "run", "lint", "--", "src/dashboard/components/PropertiesModal/index.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr

    # Check for errors specifically in our target file
    target_file_errors = [
        line for line in output.split('\n')
        if 'PropertiesModal/index.tsx' in line and 'error' in line.lower()
    ]

    assert not target_file_errors, \
        f"ESLint errors in PropertiesModal/index.tsx:\n{chr(10).join(target_file_errors[-10:])}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
