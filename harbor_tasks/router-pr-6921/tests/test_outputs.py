"""
Tests for TanStack Router staleReloadMode feature.

This feature adds:
1. LoaderStaleReloadMode type ('background' | 'blocking')
2. Object-form loader syntax with optional staleReloadMode
3. Router-level defaultStaleReloadMode option
4. Blocking stale reload behavior when configured
"""
import subprocess
import os
import json

REPO = "/workspace/router"


def run_command(cmd, cwd=REPO, timeout=300):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


# ============================================
# Fail-to-Pass Tests
# ============================================

def test_loader_stale_reload_mode_type_exported():
    """LoaderStaleReloadMode type is exported from router-core (fail_to_pass)."""
    # Check that LoaderStaleReloadMode is exported from index.ts
    result = run_command(
        ["grep", "-l", "LoaderStaleReloadMode", "packages/router-core/src/index.ts"]
    )
    assert result.returncode == 0, (
        "LoaderStaleReloadMode should be exported from router-core index.ts"
    )


def test_route_loader_object_type_exists():
    """RouteLoaderObject type is defined in route.ts (fail_to_pass)."""
    result = run_command(
        ["grep", "-l", "RouteLoaderObject", "packages/router-core/src/route.ts"]
    )
    assert result.returncode == 0, (
        "RouteLoaderObject type should be defined in route.ts"
    )


def test_default_stale_reload_mode_option_exists():
    """defaultStaleReloadMode option is defined in router.ts (fail_to_pass)."""
    result = run_command(
        ["grep", "-l", "defaultStaleReloadMode", "packages/router-core/src/router.ts"]
    )
    assert result.returncode == 0, (
        "defaultStaleReloadMode should be defined in router.ts RouterOptions"
    )


def test_load_matches_extracts_handler_from_object_loader():
    """load-matches.ts extracts handler from object-form loader (fail_to_pass)."""
    # The code should extract handler from object-form loaders
    result = run_command(
        ["grep", "routeLoader?.handler", "packages/router-core/src/load-matches.ts"]
    )
    assert result.returncode == 0, (
        "load-matches.ts should extract handler from object-form loader"
    )


def test_should_reload_in_background_variable_exists():
    """shouldReloadInBackground logic exists in load-matches.ts (fail_to_pass)."""
    result = run_command(
        ["grep", "shouldReloadInBackground", "packages/router-core/src/load-matches.ts"]
    )
    assert result.returncode == 0, (
        "load-matches.ts should have shouldReloadInBackground logic"
    )


def test_blocking_stale_reload_mode_logic():
    """Blocking stale reload mode is checked in loadRouteMatch (fail_to_pass)."""
    # Check that the blocking logic compares against 'blocking'
    result = run_command(
        ["grep", "'blocking'", "packages/router-core/src/load-matches.ts"]
    )
    assert result.returncode == 0, (
        "load-matches.ts should check for 'blocking' stale reload mode"
    )


def test_object_form_loader_in_test_file():
    """Test file demonstrates object-form loader usage (fail_to_pass).

    This test checks that the test file contains tests for the object-form
    loader syntax with staleReloadMode configuration.
    """
    test_file = os.path.join(REPO, "packages/router-core/tests/load.test.ts")
    if not os.path.exists(test_file):
        # If test file doesn't exist, skip this check
        return

    with open(test_file) as f:
        content = f.read()

    # Check for staleReloadMode tests or object-form loader tests
    has_stale_reload_mode = "staleReloadMode" in content
    has_object_loader = "handler:" in content and "loader:" in content

    assert has_stale_reload_mode or has_object_loader, (
        "Test file should contain staleReloadMode or object-form loader tests"
    )


# ============================================
# Pass-to-Pass Tests (Repo CI/CD)
# ============================================

def test_router_core_types_pass():
    """Router-core type checking passes (pass_to_pass)."""
    result = run_command(
        "CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:types --outputStyle=stream --skipRemoteCache",
        timeout=600
    )
    assert result.returncode == 0, f"Type checking failed:\n{result.stderr[-2000:]}"


def test_router_core_build_succeeds():
    """Router-core package builds successfully (pass_to_pass)."""
    result = run_command(
        "CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:build --outputStyle=stream --skipRemoteCache",
        timeout=600
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"


def test_router_core_unit_tests_pass():
    """Router-core unit tests pass (pass_to_pass)."""
    result = run_command(
        "CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:unit --outputStyle=stream --skipRemoteCache",
        timeout=600
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"


def test_router_core_eslint_passes():
    """Router-core ESLint passes (pass_to_pass)."""
    result = run_command(
        "CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:eslint --outputStyle=stream --skipRemoteCache",
        timeout=600
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-2000:]}"


def test_router_core_package_exports_valid():
    """Router-core package exports are valid (publint + attw) (pass_to_pass)."""
    result = run_command(
        "CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:build --outputStyle=stream --skipRemoteCache",
        timeout=600
    )
    assert result.returncode == 0, f"Package export validation failed:\n{result.stderr[-2000:]}"
