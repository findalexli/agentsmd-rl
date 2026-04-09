"""Tests for TanStack/router PR #7037 - fix TS4023 by converting interface to type."""
import subprocess
import re
import sys
import os

REPO = "/workspace/router"


def test_react_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/react-router/src/useBlocker.tsx")
    with open(filepath, 'r') as f:
        content = f.read()

    # Should NOT have 'interface ShouldBlockFnLocation'
    assert "interface ShouldBlockFnLocation" not in content, \
        "ShouldBlockFnLocation is still declared as interface (expected type)"

    # Should have 'type ShouldBlockFnLocation<' with '=' sign
    assert re.search(r'type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{', content), \
        "ShouldBlockFnLocation should be declared as type with '='"


def test_solid_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/solid-router/src/useBlocker.tsx")
    with open(filepath, 'r') as f:
        content = f.read()

    # Should NOT have 'interface ShouldBlockFnLocation'
    assert "interface ShouldBlockFnLocation" not in content, \
        "ShouldBlockFnLocation is still declared as interface (expected type)"

    # Should have 'type ShouldBlockFnLocation<' with '=' sign
    assert re.search(r'type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{', content), \
        "ShouldBlockFnLocation should be declared as type with '='"


def test_vue_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/vue-router/src/useBlocker.tsx")
    with open(filepath, 'r') as f:
        content = f.read()

    # Should NOT have 'interface ShouldBlockFnLocation'
    assert "interface ShouldBlockFnLocation" not in content, \
        "ShouldBlockFnLocation is still declared as interface (expected type)"

    # Should have 'type ShouldBlockFnLocation<' with '=' sign
    assert re.search(r'type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{', content), \
        "ShouldBlockFnLocation should be declared as type with '='"


def test_react_router_types_compile():
    """TypeScript compilation passes for react-router (pass-to-pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"react-router type check failed:\n{result.stderr[-1000:]}"


def test_solid_router_types_compile():
    """TypeScript compilation passes for solid-router (pass-to-pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"solid-router type check failed:\n{result.stderr[-1000:]}"


def test_vue_router_types_compile():
    """TypeScript compilation passes for vue-router (pass-to-pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"vue-router type check failed:\n{result.stderr[-1000:]}"


def test_repo_react_router_unit_tests():
    """Repo's unit tests pass for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"react-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_unit_tests():
    """Repo's unit tests pass for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit", "--run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"solid-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_unit_tests():
    """Repo's unit tests pass for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:unit", "--run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"vue-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_react_router_eslint():
    """Repo's ESLint passes for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"react-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_eslint():
    """Repo's ESLint passes for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"solid-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_eslint():
    """Repo's ESLint passes for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:eslint"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"vue-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_react_router_build():
    """Repo's build validation passes for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:build"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"react-router build test failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_build():
    """Repo's build validation passes for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:build"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"solid-router build test failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_build():
    """Repo's build validation passes for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:build"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"vue-router build test failed:\n{r.stderr[-500:]}"


def test_useblocker_type_export_regression():
    """Verify the TS4023 regression scenario is fixed (fail-to-pass).

    This tests that wrapping useBlocker in a custom hook and returning the blocker
    doesn't cause TypeScript error about unexported ShouldBlockFnLocation.
    """
    # Create a test file that triggers TS4023 with the old interface-based code
    test_file = os.path.join(REPO, "packages/react-router/src/__ts4023_test__.ts")
    # Create a custom tsconfig that only includes our test file
    tsconfig_file = os.path.join(REPO, "packages/react-router/__ts4023_tsconfig__.json")

    # This is the exact pattern that caused TS4023 before the fix
    test_content = '''
// Test that useBlocker return type doesn't reference unexported interface
import { useBlocker } from './useBlocker'

// This pattern should NOT cause TS4023 error after the fix
export const useCustomBlocker = () => {
  const blocker = useBlocker({ shouldBlockFn: () => true, withResolver: true })
  return { blocker }
}
'''

    # Custom tsconfig that extends package config but only includes test file
    tsconfig_content = '''
{
  "extends": "./tsconfig.json",
  "include": ["src/__ts4023_test__.ts"]
}
'''

    try:
        with open(test_file, 'w') as f:
            f.write(test_content)

        with open(tsconfig_file, 'w') as f:
            f.write(tsconfig_content)

        # Run TypeScript compiler with project config (important: using --project
        # ensures declaration emit is checked, unlike passing file on command line)
        result = subprocess.run(
            ["npx", "tsc", "--project", "__ts4023_tsconfig__.json", "--noEmit"],
            cwd=os.path.join(REPO, "packages/react-router"),
            capture_output=True,
            text=True,
            timeout=60
        )

        # Clean up before assertions (so cleanup happens even if assertions fail)
        os.remove(test_file)
        os.remove(tsconfig_file)

        # Check for TS4023 error in the output
        output = result.stdout + result.stderr
        if "TS4023" in output:
            assert False, "TS4023 error still present: 'ShouldBlockFnLocation' cannot be named"

        # The test should compile without the TS4023 error
        assert result.returncode == 0, \
            f"TypeScript compilation failed:\n{output}"
    except Exception:
        # Ensure cleanup on any error
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(tsconfig_file):
            os.remove(tsconfig_file)
        raise
