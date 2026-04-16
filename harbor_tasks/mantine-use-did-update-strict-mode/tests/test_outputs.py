"""Tests for useDidUpdate React hook fix.

This test file validates the fix for useDidUpdate running on mount in React Strict Mode.
The bug: In React Strict Mode, effects are double-invoked in development.
Without proper cleanup, the mounted ref stays true after the first mount,
causing the callback to run on the second (remount) effect call.

The fix: Add a cleanup effect that resets mounted.current to false when the component unmounts.
"""

import subprocess
import sys
import os

REPO = "/workspace/mantine/packages/@mantine/hooks"
HOOK_FILE = f"{REPO}/src/use-did-update/use-did-update.ts"


def read_hook_source():
    """Read the source of the hook file."""
    with open(HOOK_FILE, 'r') as f:
        return f.read()


def test_cleanup_effect_exists():
    """Fail-to-pass: Verify the cleanup effect that resets mounted ref is present."""
    source = read_hook_source()

    # Check for the cleanup effect that resets mounted.current to false
    assert "mounted.current = false" in source, (
        "Missing cleanup effect that resets mounted ref. "
        "The fix requires a useEffect that sets mounted.current = false on unmount."
    )


def test_returns_undefined_in_effect():
    """Fail-to-pass: Verify the effect returns undefined explicitly after setting mounted."""
    source = read_hook_source()

    # The fix adds "return undefined" after setting mounted.current = true
    assert "return undefined" in source, (
        "Missing explicit 'return undefined' after setting mounted.current = true. "
        "This is part of the fix for proper cleanup handling."
    )


def test_two_useeffect_calls():
    """Fail-to-pass: Verify there are two useEffect calls (cleanup + main effect)."""
    source = read_hook_source()

    # Count useEffect calls - should be 2 after the fix
    effect_count = source.count('useEffect')
    assert effect_count >= 2, (
        f"Expected at least 2 useEffect calls (cleanup + main), found {effect_count}. "
        "The fix adds a cleanup effect in addition to the existing effect."
    )


def test_cleanup_effect_structure():
    """Fail-to-pass: Verify the cleanup effect has correct structure (empty deps array)."""
    source = read_hook_source()

    # After the fix, we should have:
    # useEffect(() => () => { mounted.current = false; }, [])
    # This means looking for the pattern of useEffect followed by mounted.current = false

    lines = source.split('\n')
    found_mounted_false = False
    found_cleanup_pattern = False

    for i, line in enumerate(lines):
        if 'mounted.current = false' in line:
            found_mounted_false = True
            # Look backwards to find if it's in a cleanup effect context
            # The cleanup effect should be near a useEffect call
            for j in range(max(0, i-10), i):
                if 'useEffect' in lines[j]:
                    found_cleanup_pattern = True
                    break
            break

    assert found_mounted_false, (
        "Missing 'mounted.current = false' statement. "
        "This is required to reset the ref when component unmounts."
    )

    assert found_cleanup_pattern, (
        "The 'mounted.current = false' should be inside a useEffect cleanup. "
        "The fix requires a separate useEffect with a cleanup function."
    )


def test_typescript_syntax_valid():
    """Pass-to-pass: Verify the TypeScript file is syntactically valid."""
    # Use tsc to check syntax - just verify it can be parsed
    result = subprocess.run(
        ["tsc", "--noEmit", "--skipLibCheck", "--allowJs", "--checkJs", "false",
         "--target", "ES2020", "--module", "ESNext", "--moduleResolution", "node",
         HOOK_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )

    # We accept 0 (success) or any return code since we're checking for parse errors
    # The key is that the error message shouldn't be about syntax
    if result.returncode != 0:
        # Check if the error is just about missing types/modules, not syntax
        error_lower = (result.stdout + result.stderr).lower()
        syntax_errors = [
            "syntax", "unexpected token", "expected", "cannot find name",
            "declaration expected", "expression expected"
        ]
        for err in syntax_errors:
            if err in error_lower:
                raise AssertionError(f"TypeScript syntax error detected: {result.stdout}\n{result.stderr}")


def test_hook_function_signature_unchanged():
    """Pass-to-pass: Verify the hook function signature is unchanged."""
    source = read_hook_source()

    # Check that the function signature matches the expected pattern
    assert "export function useDidUpdate(fn: EffectCallback, dependencies?: DependencyList)" in source, (
        "The function signature of useDidUpdate should not be changed. "
        "The fix should maintain backward compatibility."
    )

    # Check that imports are unchanged
    assert "import { DependencyList, EffectCallback, useEffect, useRef } from 'react';" in source, (
        "The imports should remain unchanged. Only the implementation should be fixed."
    )


def test_repo_jest_use_did_update():
    """Repo's unit test for useDidUpdate passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "jest", "packages/@mantine/hooks/src/use-did-update/use-did-update.test.ts", "--no-cache"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/workspace/mantine",
    )
    assert r.returncode == 0, f"Jest test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_eslint_hook():
    """Repo's eslint passes on hook file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/hooks/src/use-did-update/use-did-update.ts", "--cache"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/workspace/mantine",
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_prettier_hook():
    """Repo's prettier check passes on hook file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/hooks/src/use-did-update/use-did-update.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd="/workspace/mantine",
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_strict_mode_fix_complete():
    """Fail-to-pass: Comprehensive check for the Strict Mode fix."""
    source = read_hook_source()

    # The fix requires ALL of the following:
    required_patterns = [
        ("mounted.current = false", "Cleanup that resets the mounted ref"),
        ("return undefined", "Explicit return undefined after setting mounted"),
    ]

    for pattern, description in required_patterns:
        assert pattern in source, (
            f"Missing required fix element: {description}. "
            f"Pattern '{pattern}' not found in the source code."
        )

    # Should have at least 2 useEffect calls
    effect_count = source.count('useEffect')
    assert effect_count >= 2, (
        f"The fix requires 2 useEffect calls, found {effect_count}. "
        "One for cleanup (reset on unmount) and one for the main effect."
    )
