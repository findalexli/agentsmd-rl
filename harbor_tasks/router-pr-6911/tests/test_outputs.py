"""
Tests for TanStack Router solid-router MatchRoute reactivity fix.

This PR fixes a bug where MatchRoute component and useMatchRoute hook in solid-router
lose reactivity - route changes leave render-prop or plain children "stuck on the
initial match result" instead of updating properly.

The fix moves opts destructuring into the createMemo scope and wraps renderedChild
in Solid.createMemo() to properly track reactive dependencies.
"""
import subprocess
import os
import re

REPO = "/workspace/router"


def test_usematchroute_reactive_opts():
    """
    useMatchRoute properly tracks reactive opts (fail_to_pass).

    This verifies that useMatchRoute reads opts inside createMemo so that
    changes to to/params are tracked reactively.

    In the buggy version, destructuring happens BEFORE createMemo:
        const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
        return Solid.createMemo(() => { ... })

    In the fixed version, destructuring happens INSIDE createMemo:
        return Solid.createMemo(() => {
            const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
            ...
        })
    """
    matches_file = os.path.join(REPO, "packages/solid-router/src/Matches.tsx")
    with open(matches_file, 'r') as f:
        content = f.read()

    # The buggy pattern: destructuring outside memo then returning memo
    buggy_pattern = r'const\s*\{\s*pending.*\}\s*=\s*opts\s*\n\s*return\s+Solid\.createMemo'

    # The fixed pattern: memo first, then destructuring inside
    fixed_pattern = r'return\s+Solid\.createMemo\(\(\)\s*=>\s*\{\s*\n\s*const\s*\{\s*pending'

    has_buggy = re.search(buggy_pattern, content) is not None
    has_fixed = re.search(fixed_pattern, content) is not None

    assert not has_buggy, "Bug still present: opts destructuring is outside createMemo"
    assert has_fixed, "Fix not applied: opts destructuring should be inside createMemo"


def test_matchroute_uses_creatememo():
    """
    MatchRoute uses Solid.createMemo for renderedChild (fail_to_pass).

    The fix wraps renderedChild in Solid.createMemo() instead of being
    a plain function, so Solid can track the reactive dependencies.

    Buggy: const renderedChild = () => { ... }
    Fixed: const renderedChild = Solid.createMemo(() => { ... })
    """
    matches_file = os.path.join(REPO, "packages/solid-router/src/Matches.tsx")
    with open(matches_file, 'r') as f:
        content = f.read()

    # Check that renderedChild is defined with createMemo
    assert "const renderedChild = Solid.createMemo(" in content, (
        "MatchRoute should wrap renderedChild in Solid.createMemo"
    )

    # Check that it returns the memo wrapped in a fragment
    assert "return <>{renderedChild()}</>" in content, (
        "MatchRoute should return renderedChild wrapped in a fragment"
    )


def test_matchroute_child_inside_memo():
    """
    MatchRoute reads props.children inside memo (fail_to_pass).

    For proper reactivity, props.children must be accessed inside the
    createMemo callback, not outside it.

    Buggy:
        const child = props.children
        const renderedChild = () => { ... use child ... }

    Fixed:
        const renderedChild = Solid.createMemo(() => {
            const child = props.children  // inside memo
            ...
        })
    """
    matches_file = os.path.join(REPO, "packages/solid-router/src/Matches.tsx")
    with open(matches_file, 'r') as f:
        content = f.read()

    # Find the MatchRoute function body
    match = re.search(r'export function MatchRoute.*?\n\}', content, re.DOTALL)
    assert match, "Could not find MatchRoute function"

    matchroute_body = match.group(0)

    # The buggy pattern: "const child = props.children" before the memo
    # This reads the prop value once at render time, not reactively
    buggy_child_outside = re.search(
        r'const child = props\.children\s*\n\s*const renderedChild = \(\)',
        matchroute_body
    )

    # The fixed pattern: child is read inside the memo
    fixed_child_inside = re.search(
        r'createMemo\(\(\)\s*=>\s*\{[^}]*const child = props\.children',
        matchroute_body,
        re.DOTALL
    )

    assert not buggy_child_outside, (
        "Bug present: props.children is read outside the memo"
    )
    assert fixed_child_inside, (
        "Fix not applied: props.children should be read inside createMemo"
    )


def test_matchroute_returns_fragment():
    """
    MatchRoute returns renderedChild wrapped in a fragment (fail_to_pass).

    The fix changes from `return renderedChild()` to `return <>{renderedChild()}</>`.
    This ensures proper JSX rendering in Solid.
    """
    matches_file = os.path.join(REPO, "packages/solid-router/src/Matches.tsx")
    with open(matches_file, 'r') as f:
        content = f.read()

    # Find the MatchRoute function
    match = re.search(r'export function MatchRoute.*?\n\}', content, re.DOTALL)
    assert match, "Could not find MatchRoute function"

    matchroute_body = match.group(0)

    # Should NOT have plain return renderedChild()
    assert "return renderedChild()" not in matchroute_body or "<>{renderedChild()}</>" in matchroute_body, (
        "MatchRoute should return renderedChild wrapped in a JSX fragment"
    )

    # Should have fragment wrapper
    assert "<>{renderedChild()}</>" in matchroute_body, (
        "MatchRoute should return <>{renderedChild()}</>"
    )


def test_solid_router_types():
    """
    solid-router type checking passes (pass_to_pass).
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:types"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Type checking failed.\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )


def test_solid_router_builds():
    """
    solid-router package builds successfully (pass_to_pass).
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:build"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build failed.\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )


def test_solid_router_eslint():
    """
    solid-router ESLint passes (pass_to_pass).
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"ESLint failed.\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )


def test_solid_router_unit_matches():
    """
    solid-router Matches.test.tsx unit tests pass (pass_to_pass).

    This runs the unit tests for the Matches component, which is the file
    modified by the PR. These tests verify useMatches, useMatchRoute, and
    MatchRoute functionality.
    """
    result = subprocess.run(
        [
            "pnpm", "vitest", "run", "tests/Matches.test.tsx"
        ],
        cwd=f"{REPO}/packages/solid-router",
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1"}
    )

    assert result.returncode == 0, (
        f"Matches unit tests failed.\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )


def test_solid_router_test_build():
    """
    solid-router build validation passes (pass_to_pass).

    Runs publint and attw to validate the built package exports are correct.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:build"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build validation failed.\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )
