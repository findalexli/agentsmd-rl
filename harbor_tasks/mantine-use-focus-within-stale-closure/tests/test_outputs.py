"""Tests for use-focus-within stale closure fix.

This task tests the fix for a React hook stale closure bug in useFocusWithin.
The bug: onFocus/onBlur callbacks captured stale state due to useCallback
dependency arrays not updating when the callbacks changed.

The fix: Use useCallbackRef to always get the latest callback reference.
"""

import subprocess
import sys

REPO = "/workspace/mantine"
HOOKS_DIR = f"{REPO}/packages/@mantine/hooks"


def test_use_focus_within_file_exists():
    """Target file exists and is readable."""
    import os
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, 'r') as f:
        content = f.read()
    assert 'useFocusWithin' in content, "Hook not found in file"


def test_use_callback_ref_imported():
    """Fix: useCallbackRef is imported from utils (fail-to-pass)."""
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    with open(path, 'r') as f:
        content = f.read()
    assert 'useCallbackRef' in content, "useCallbackRef not imported - stale closure fix missing"


def test_onfocus_uses_callbackref():
    """Fix: onFocus callback uses useCallbackRef wrapper (fail-to-pass)."""
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    with open(path, 'r') as f:
        content = f.read()
    # Check for the pattern: onFocusRef = useCallbackRef(onFocus)
    assert 'onFocusRef = useCallbackRef(onFocus)' in content, \
        "onFocus not wrapped with useCallbackRef - stale closure bug present"


def test_onblur_uses_callbackref():
    """Fix: onBlur callback uses useCallbackRef wrapper (fail-to-pass)."""
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    with open(path, 'r') as f:
        content = f.read()
    # Check for the pattern: onBlurRef = useCallbackRef(onBlur)
    assert 'onBlurRef = useCallbackRef(onBlur)' in content, \
        "onBlur not wrapped with useCallbackRef - stale closure bug present"


def test_handle_focus_in_no_deps():
    """Fix: handleFocusIn useCallback has empty deps (fail-to-pass)."""
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    with open(path, 'r') as f:
        content = f.read()
    # After fix, handleFocusIn should have empty dependency array
    # We need to verify the onFocus dependency was removed
    import re
    # Find handleFocusIn definition
    match = re.search(r'const handleFocusIn = useCallback\(\(event: FocusEvent\) => \{[^}]+\},\s*(\[[^\]]*\])', content)
    if match:
        deps = match.group(1)
        assert deps == '[]', f"handleFocusIn still has dependencies: {deps} - stale closure risk"
    else:
        # Alternative pattern - function defined differently
        pass


def test_handle_focus_out_no_deps():
    """Fix: handleFocusOut useCallback has empty deps (fail-to-pass)."""
    path = f"{HOOKS_DIR}/src/use-focus-within/use-focus-within.ts"
    with open(path, 'r') as f:
        content = f.read()
    import re
    # Find handleFocusOut definition
    match = re.search(r'const handleFocusOut = useCallback\(\(event: FocusEvent\) => \{[^}]+\},\s*(\[[^\]]*\])', content)
    if match:
        deps = match.group(1)
        assert deps == '[]', f"handleFocusOut still has dependencies: {deps} - stale closure risk"
    else:
        # Alternative pattern - function defined differently
        pass


def test_hooks_jest_passes():
    """Repo's Jest tests for @mantine/hooks pass (fail-to-pass for fix)."""
    # Run only the use-focus-within tests
    result = subprocess.run(
        ["yarn", "jest", "--testPathPatterns=use-focus-within", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Jest tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_hooks_typescript_compiles():
    """TypeScript compiles without errors (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/@mantine/hooks/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-500:]}"


def test_use_callback_ref_util_exists():
    """useCallbackRef utility exists and is exportable (pass-to-pass)."""
    # Check that useCallbackRef is available from utils
    util_path = f"{HOOKS_DIR}/src/utils/index.ts"
    if __import__('os').path.exists(util_path):
        with open(util_path, 'r') as f:
            content = f.read()
        assert 'useCallbackRef' in content, "useCallbackRef not exported from utils"


def test_hooks_eslint_passes():
    """ESLint passes on @mantine/hooks package (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "eslint", "packages/@mantine/hooks/src"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_hooks_prettier_passes():
    """Prettier formatting check passes on hooks package (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "prettier", "--check", "packages/@mantine/hooks/src/**/*.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_related_hooks_jest_passes():
    """Jest tests for related hooks pass (pass_to_pass)."""
    # Run tests for hooks similar to use-focus-within (event-based hooks)
    result = subprocess.run(
        ["yarn", "jest",
         "packages/@mantine/hooks/src/use-hover/use-hover.test.tsx",
         "packages/@mantine/hooks/src/use-click-outside/use-click-outside.test.tsx",
         "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Related hooks Jest tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_hooks_stylelint_passes():
    """Stylelint passes on @mantine/hooks package (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "stylelint", "packages/@mantine/hooks/**/*.css"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Stylelint failed:\n{result.stderr[-500:]}"
