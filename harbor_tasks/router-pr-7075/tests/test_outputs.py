"""
Tests for TanStack Router PR #7075: stop preload after beforeLoad errors

This PR fixes a bug where child route handlers (beforeLoad, head) would
continue executing even after a parent route's beforeLoad handler failed
during preload operations.
"""

import subprocess
import os
import sys
import re

REPO = "/workspace/router"


def test_preload_error_stops_child_handlers():
    """
    Verify the fix: when parent beforeLoad throws during preload,
    child beforeLoad should not be called (fail_to_pass).

    This test creates a temporary test file and runs it to verify the behavior.
    """
    # Create a standalone test that imports and tests the core behavior
    # Uses same patterns as existing load.test.ts
    test_code = '''
import { describe, test, expect, vi } from 'vitest'
import { createMemoryHistory } from '@tanstack/history'
import { BaseRootRoute, BaseRoute } from '../src'
import { createTestRouter } from './routerTestUtils'
import type { RootRouteOptions } from '../src'

type AnyRouteOptions = RootRouteOptions<any>
type BeforeLoad = NonNullable<AnyRouteOptions['beforeLoad']>

describe('preload error handling', () => {
  test('parent beforeLoad error during preload stops child handlers', async () => {
    const parentBeforeLoad = vi.fn<BeforeLoad>(async ({ preload }) => {
      if (preload) throw new Error('parent preload error')
    })
    const childBeforeLoad = vi.fn<BeforeLoad>()
    const parentHead = vi.fn(() => ({ meta: [{ title: 'Parent' }] }))
    const childHead = vi.fn(() => ({ meta: [{ title: 'Child' }] }))

    const rootRoute = new BaseRootRoute({})
    const parentRoute = new BaseRoute({
      getParentRoute: () => rootRoute,
      path: '/parent',
      beforeLoad: parentBeforeLoad,
      head: parentHead,
    })
    const childRoute = new BaseRoute({
      getParentRoute: () => parentRoute,
      path: '/child',
      beforeLoad: childBeforeLoad,
      head: childHead,
    })

    const routeTree = rootRoute.addChildren([
      parentRoute.addChildren([childRoute])
    ])

    const router = createTestRouter({
      routeTree,
      history: createMemoryHistory(),
    })

    // Preload should trigger the parent error
    await router.preloadRoute({ to: '/parent/child' })

    // Parent handlers should be called
    expect(parentBeforeLoad).toHaveBeenCalledTimes(1)
    expect(parentHead).toHaveBeenCalledTimes(1)

    // Child handlers should NOT be called because parent failed
    expect(childBeforeLoad).not.toHaveBeenCalled()
    expect(childHead).not.toHaveBeenCalled()
  })
})
'''

    test_file = os.path.join(REPO, "packages/router-core/tests/preload-fix.test.ts")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--",
             "tests/preload-fix.test.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )

        assert result.returncode == 0, f"Preload fix test failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_break_condition_includes_firstbadmatchindex():
    """
    Verify the break condition in the preload loop includes firstBadMatchIndex check (fail_to_pass).

    The fix changes the loop break condition from:
        if (inner.serialError) { break }
    to:
        if (inner.serialError || inner.firstBadMatchIndex != null) { break }
    """
    load_matches_path = os.path.join(REPO, "packages/router-core/src/load-matches.ts")

    with open(load_matches_path, 'r') as f:
        content = f.read()

    # Look for the specific pattern: break condition combining serialError with firstBadMatchIndex
    # The fix adds "|| inner.firstBadMatchIndex != null" to the break condition
    pattern = r'if\s*\(\s*inner\.serialError\s*\|\|\s*inner\.firstBadMatchIndex\s*!=\s*null\s*\)'
    match = re.search(pattern, content)

    assert match is not None, \
        "Missing the fix: break condition should be 'if (inner.serialError || inner.firstBadMatchIndex != null)'"


def test_headmaxindex_uses_firstbadmatchindex_directly():
    """
    Verify headMaxIndex is calculated using firstBadMatchIndex directly (fail_to_pass).

    The fix changes from:
        let headMaxIndex = inner.serialError ? (inner.firstBadMatchIndex ?? 0) : inner.matches.length - 1
    to:
        let headMaxIndex = inner.firstBadMatchIndex !== undefined ? inner.firstBadMatchIndex : inner.matches.length - 1
    """
    load_matches_path = os.path.join(REPO, "packages/router-core/src/load-matches.ts")

    with open(load_matches_path, 'r') as f:
        content = f.read()

    # The fix should use firstBadMatchIndex !== undefined as the condition, NOT serialError
    # Look for the pattern where headMaxIndex assignment uses firstBadMatchIndex as the condition
    pattern = r'headMaxIndex\s*=\s*\n?\s*inner\.firstBadMatchIndex\s*!==\s*undefined'
    match = re.search(pattern, content)

    assert match is not None, \
        "headMaxIndex should use 'inner.firstBadMatchIndex !== undefined' as condition, not 'inner.serialError'"


def test_router_core_type_check():
    """Run TypeScript type checking on router-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type check failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"


def test_router_core_eslint():
    """Run ESLint on router-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"ESLint failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"


def test_router_core_build():
    """Build router-core package (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"


def test_router_core_all_unit_tests():
    """Run all router-core unit tests (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"


def test_router_core_package_quality():
    """Run publint and attw package quality checks (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Package quality check failed:\nstdout:\n{result.stdout[-2000:]}\nstderr:\n{result.stderr[-2000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
