"""
Tests for TanStack/router PR #6911: Fix MatchRoute reactivity in Solid Router

This PR fixes a bug where MatchRoute components did not properly react to:
1. Navigation changes (router.history.push)
2. Reactive params changes (via Solid signals)

The fix moves option destructuring inside Solid.createMemo so reactive
inputs are tracked correctly.
"""

import subprocess
import os
import sys
import pytest

REPO = "/workspace/router"
SOLID_ROUTER_PACKAGE = os.path.join(REPO, "packages/solid-router")
MATCHES_FILE = os.path.join(SOLID_ROUTER_PACKAGE, "src/Matches.tsx")


def test_repo_unit_tests():
    """Solid Router unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_repo_type_tests():
    """Solid Router type tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_usematchroute_opts_inside_memo():
    """
    useMatchRoute destructures opts inside createMemo (fail_to_pass).

    Before the fix, opts were destructured outside createMemo, so reactive
    changes to 'to' and 'params' were not tracked. After the fix, the
    destructuring happens inside the memo callback.
    """
    with open(MATCHES_FILE, 'r') as f:
        content = f.read()

    # Find the useMatchRoute function and check that opts destructuring
    # happens inside createMemo, not outside

    # Look for the pattern where createMemo callback starts with destructuring
    lines = content.split('\n')
    in_usematchroute = False
    found_creatememo = False
    checked_destructure_location = False

    for i, line in enumerate(lines):
        # Detect we're in useMatchRoute function
        if 'export function useMatchRoute' in line:
            in_usematchroute = True
            continue

        if in_usematchroute:
            # Look for createMemo
            if 'Solid.createMemo' in line or 'createMemo' in line:
                found_creatememo = True
                continue

            if found_creatememo:
                # Check the next few lines for destructuring pattern
                for j in range(i, min(i + 5, len(lines))):
                    if 'const { pending, caseSensitive, fuzzy, includeSearch' in lines[j]:
                        # Found it inside createMemo - this is correct
                        checked_destructure_location = True
                        break
                    if 'router.stores.matchRouteReactivity' in lines[j]:
                        # If we hit this before finding destructuring, it's wrong
                        break
                break

    assert checked_destructure_location, (
        "opts destructuring should be inside createMemo callback in useMatchRoute. "
        "The fix requires moving `const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts` "
        "inside the Solid.createMemo callback so reactive inputs are tracked."
    )


def test_matchroute_uses_memo_for_children():
    """
    MatchRoute wraps children rendering in Solid.createMemo (fail_to_pass).

    Before the fix, renderedChild was a plain function and child was captured
    outside the reactive scope. After the fix, it's wrapped in createMemo
    and child is accessed inside the reactive scope.
    """
    with open(MATCHES_FILE, 'r') as f:
        content = f.read()

    # Check that renderedChild uses Solid.createMemo
    assert 'const renderedChild = Solid.createMemo' in content, (
        "MatchRoute should wrap renderedChild in Solid.createMemo. "
        "The fix requires changing `const renderedChild = () => {...}` to "
        "`const renderedChild = Solid.createMemo(() => {...})`"
    )

    # Check that child is accessed inside the memo (not outside)
    lines = content.split('\n')
    in_matchroute = False
    found_renderedchild_memo = False
    child_inside_memo = False

    for i, line in enumerate(lines):
        if 'export function MatchRoute' in line:
            in_matchroute = True
            continue

        if in_matchroute:
            if 'const renderedChild = Solid.createMemo' in line:
                found_renderedchild_memo = True
                # Check the next several lines for child destructuring
                for j in range(i, min(i + 10, len(lines))):
                    if 'const child = props.children' in lines[j]:
                        child_inside_memo = True
                        break
                    # Stop if we see the end of the memo callback
                    if lines[j].strip() == '})' and j > i + 2:
                        break
                break

    assert found_renderedchild_memo, "MatchRoute should use Solid.createMemo for renderedChild"
    assert child_inside_memo, (
        "`const child = props.children` should be inside the Solid.createMemo callback "
        "so that reactive changes to children are tracked."
    )


def test_matchroute_returns_jsx_fragment():
    """
    MatchRoute returns JSX fragment instead of function call (fail_to_pass).

    Before the fix: `return renderedChild()`
    After the fix: `return <>{renderedChild()}</>`
    """
    with open(MATCHES_FILE, 'r') as f:
        content = f.read()

    # Check that it returns JSX fragment syntax
    assert 'return <>{renderedChild()}</>' in content, (
        "MatchRoute should return JSX fragment `<>{renderedChild()}</>` instead of "
        "just `renderedChild()`. This ensures proper Solid reactivity tracking."
    )


def test_solid_build_passes():
    """Solid Router package builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_repo_build_validation():
    """Solid Router package validation passes (publint + attw) (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build validation failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_repo_eslint():
    """Solid Router passes ESLint checks (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
