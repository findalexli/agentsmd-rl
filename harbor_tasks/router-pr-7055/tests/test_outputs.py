"""
Tests for TanStack Router scroll restoration fix (PR #7055).

The bug: Browser forward navigation fails to restore scroll position because
the scroll cache is incorrectly cleared before restoration can occur.

The fix: Remove the code that clears the scroll cache on forward navigation.
"""
import subprocess
import os
import re

REPO = "/workspace/router"
E2E_DIR = os.path.join(REPO, "e2e/react-router/scroll-restoration-sandbox-vite")
SCROLL_RESTORATION_FILE = os.path.join(REPO, "packages/router-core/src/scroll-restoration.ts")


def test_forward_navigation_does_not_clear_cache():
    """
    Fail-to-pass: The scroll cache should NOT be cleared on forward navigation.

    The buggy code pattern checks if toIndex > fromIndex (forward navigation)
    and clears the cache. This breaks scroll restoration on forward nav.
    After the fix, this pattern should not exist.
    """
    with open(SCROLL_RESTORATION_FILE, 'r') as f:
        content = f.read()

    # The buggy code has this specific pattern that determines forward navigation
    # and then clears the cache. After the fix, this logic is removed.
    buggy_pattern = re.compile(
        r'const\s+shouldClearCache\s*=.*toIndex\s*>\s*fromIndex',
        re.DOTALL
    )

    # Also check for the cache clearing in the onRendered context
    cache_clear_pattern = re.compile(
        r'if\s*\(\s*shouldClearCache\s*\)\s*\{[^}]*delete\s+state\[cacheKey\]',
        re.DOTALL
    )

    has_buggy_logic = bool(buggy_pattern.search(content))
    has_cache_clear = bool(cache_clear_pattern.search(content))

    assert not (has_buggy_logic and has_cache_clear), (
        "Buggy scroll cache clearing logic still present. "
        "Forward navigation should not clear the scroll restoration cache."
    )


def test_scroll_restoration_module_imports():
    """
    Fail-to-pass: The scroll-restoration module should be importable and
    setupScrollRestoration should be exported.

    This verifies the fix doesn't break the module structure.
    """
    with open(SCROLL_RESTORATION_FILE, 'r') as f:
        content = f.read()

    # Verify key exports exist
    assert 'export function setupScrollRestoration' in content, (
        "setupScrollRestoration function should be exported"
    )
    assert 'export const scrollRestorationCache' in content, (
        "scrollRestorationCache should be exported"
    )
    assert 'export const defaultGetScrollRestorationKey' in content, (
        "defaultGetScrollRestorationKey should be exported"
    )


def test_scroll_restoration_preserves_cache_structure():
    """
    Fail-to-pass: After the fix, the cache should still be properly initialized
    and managed, just not cleared on forward navigation.
    """
    with open(SCROLL_RESTORATION_FILE, 'r') as f:
        content = f.read()

    # The fix should preserve the cache initialization in onRendered
    # This pattern should still exist after the fix
    cache_init_pattern = re.compile(
        r"cache\.set\(\s*\(state\)\s*=>\s*\{[^}]*state\[cacheKey\]\s*\|\|=",
        re.DOTALL
    )

    assert cache_init_pattern.search(content), (
        "Cache initialization pattern should still exist in onRendered. "
        "The fix should only remove the cache clearing, not the initialization."
    )


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript compilation should succeed.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:build", "--skip-nx-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"TypeScript build failed:\n{result.stderr[-2000:]}"


def test_router_core_types():
    """
    Pass-to-pass: TypeScript type checking should pass for router-core.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types", "--skip-nx-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type checking failed:\n{result.stderr[-2000:]}"


def test_no_syntax_errors_in_scroll_restoration():
    """
    Pass-to-pass: The scroll-restoration.ts file should have valid TypeScript syntax.
    """
    # Quick syntax check using tsc --noEmit on just this file
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "--target", "ES2020",
         "--module", "ESNext",
         "--moduleResolution", "bundler",
         SCROLL_RESTORATION_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # Note: This may fail due to imports, so we just check for syntax errors
    if result.returncode != 0:
        stderr = result.stderr.lower()
        # Ignore import resolution errors, focus on syntax
        if 'syntax' in stderr or 'unexpected' in stderr or 'expected' in stderr:
            assert False, f"Syntax error in scroll-restoration.ts:\n{result.stderr}"


def test_scroll_restoration_event_handlers_exist():
    """
    Pass-to-pass: Core scroll restoration event handlers should still be set up.
    """
    with open(SCROLL_RESTORATION_FILE, 'r') as f:
        content = f.read()

    # These subscriptions should exist regardless of the bug fix
    assert "router.subscribe('onBeforeLoad'" in content, (
        "onBeforeLoad subscription should exist for snapshot handling"
    )
    assert "router.subscribe('onRendered'" in content, (
        "onRendered subscription should exist for scroll restoration"
    )
    assert "document.addEventListener('scroll'" in content, (
        "Scroll event listener should be set up"
    )
    assert "window.addEventListener('pagehide'" in content, (
        "Pagehide listener should persist scroll state"
    )


def test_ignore_scroll_flag_handling():
    """
    Fail-to-pass: After the fix, shouldClearCache logic should not exist in the
    onRendered handler. The buggy code has this pattern where it calculates
    shouldClearCache and then conditionally clears the cache before restoring.
    """
    with open(SCROLL_RESTORATION_FILE, 'r') as f:
        content = f.read()

    # Find the section from onRendered subscription to the end of the function
    on_rendered_start = content.find("router.subscribe('onRendered'")
    assert on_rendered_start != -1, "onRendered subscription should exist"

    # Get the content after onRendered subscription
    on_rendered_section = content[on_rendered_start:]

    # In the buggy version, shouldClearCache is calculated and used to clear cache
    # This should NOT be present after the fix
    has_clear_cache_logic = 'shouldClearCache' in on_rendered_section

    assert not has_clear_cache_logic, (
        "After fix, shouldClearCache logic should not appear in the onRendered handler. "
        "The cache clearing was incorrectly preventing scroll restoration on forward navigation."
    )


def test_repo_eslint():
    """
    Pass-to-pass: ESLint check for router-core passes.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint", "--skip-nx-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-2000:]}"


def test_repo_build_check():
    """
    Pass-to-pass: Package build check (publint/attw) for router-core passes.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build", "--skip-nx-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build check failed:\n{result.stderr[-2000:]}"


def test_repo_unit_tests():
    """
    Pass-to-pass: Router-core unit tests pass.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--skip-nx-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"
