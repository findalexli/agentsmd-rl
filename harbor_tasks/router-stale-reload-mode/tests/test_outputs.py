#!/usr/bin/env python3
"""
Test outputs for TanStack Router staleReloadMode feature.

This validates that the staleReloadMode feature is correctly implemented:
1. Types are exported (LoaderStaleReloadMode, RouteLoaderEntry)
2. Object-form loader with handler works
3. Blocking mode waits for stale reloads
4. Background mode (default) reloads in background
5. Router defaultStaleReloadMode works
6. Loader-level staleReloadMode overrides router default
"""

import subprocess
import sys
import os

REPO = "/workspace/router"

def run_nx_test(test_pattern=None, timeout=120):
    """Run router-core tests via nx."""
    cmd = [
        "pnpm", "nx", "run", "@tanstack/router-core:test:unit",
        "--outputStyle=stream", "--skipRemoteCache"
    ]
    if test_pattern:
        cmd.extend(["--", test_pattern])

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    return result

def test_types_exported():
    """LoaderStaleReloadMode and RouteLoaderEntry types are exported."""
    index_file = os.path.join(REPO, "packages/router-core/src/index.ts")
    with open(index_file, 'r') as f:
        content = f.read()

    assert "LoaderStaleReloadMode" in content, "LoaderStaleReloadMode not exported"
    assert "RouteLoaderEntry" in content, "RouteLoaderEntry not exported"

def test_route_loader_object_type_exists():
    """RouteLoaderObject type is defined in route.ts."""
    route_file = os.path.join(REPO, "packages/router-core/src/route.ts")
    with open(route_file, 'r') as f:
        content = f.read()

    assert "RouteLoaderObject" in content, "RouteLoaderObject type not found"
    assert "staleReloadMode?: LoaderStaleReloadMode" in content, "staleReloadMode property not found"

def test_resolve_route_loader_fn_type_exists():
    """ResolveRouteLoaderFn type helper is defined."""
    route_file = os.path.join(REPO, "packages/router-core/src/route.ts")
    with open(route_file, 'r') as f:
        content = f.read()

    assert "ResolveRouteLoaderFn" in content, "ResolveRouteLoaderFn type not found"

def test_loader_stale_reload_mode_type_defined():
    """LoaderStaleReloadMode type is defined as 'background' | 'blocking'."""
    route_file = os.path.join(REPO, "packages/router-core/src/route.ts")
    with open(route_file, 'r') as f:
        content = f.read()

    # Look for the type definition
    assert "export type LoaderStaleReloadMode = 'background' | 'blocking'" in content, \
        "LoaderStaleReloadMode type definition not found"

def test_router_options_has_default_stale_reload_mode():
    """RouterOptions interface has defaultStaleReloadMode property."""
    router_file = os.path.join(REPO, "packages/router-core/src/router.ts")
    with open(router_file, 'r') as f:
        content = f.read()

    assert "defaultStaleReloadMode?: LoaderStaleReloadMode" in content, \
        "defaultStaleReloadMode not found in RouterOptions"

def test_load_matches_handles_object_loader():
    """load-matches.ts extracts handler from object-form loader."""
    load_matches_file = os.path.join(REPO, "packages/router-core/src/load-matches.ts")
    with open(load_matches_file, 'r') as f:
        content = f.read()

    # Check for handler extraction
    assert "typeof routeLoader === 'function' ? routeLoader : routeLoader?.handler" in content, \
        "Object loader handler extraction not found"

def test_load_matches_uses_should_reload_in_background():
    """load-matches.ts uses shouldReloadInBackground flag."""
    load_matches_file = os.path.join(REPO, "packages/router-core/src/load-matches.ts")
    with open(load_matches_file, 'r') as f:
        content = f.read()

    assert "shouldReloadInBackground" in content, \
        "shouldReloadInBackground flag not found"

def test_load_matches_respects_stale_reload_mode():
    """load-matches.ts checks shouldReloadInBackground before early return."""
    load_matches_file = os.path.join(REPO, "packages/router-core/src/load-matches.ts")
    with open(load_matches_file, 'r') as f:
        content = f.read()

    # The check for prevMatch.status === 'success' should also check shouldReloadInBackground
    assert "prevMatch.status === 'success' &&" in content and \
           "shouldReloadInBackground" in content, \
        "shouldReloadInBackground not checked in stale data early return"

def test_fileroute_uses_route_loader_entry():
    """fileRoute.ts files use RouteLoaderEntry instead of RouteLoaderFn."""
    react_fileroute = os.path.join(REPO, "packages/react-router/src/fileRoute.ts")
    solid_fileroute = os.path.join(REPO, "packages/solid-router/src/fileRoute.ts")
    vue_fileroute = os.path.join(REPO, "packages/vue-router/src/fileRoute.ts")

    for path in [react_fileroute, solid_fileroute, vue_fileroute]:
        with open(path, 'r') as f:
            content = f.read()
        assert "RouteLoaderEntry" in content, f"RouteLoaderEntry not found in {path}"
        # Should not have RouteLoaderFn anymore in the imports
        lines = content.split('\n')
        import_lines = [l for l in lines if 'RouteLoaderFn' in l and 'import' in l]
        # The import should use RouteLoaderEntry, not RouteLoaderFn
        for line in import_lines:
            assert "RouteLoaderEntry" in line, f"RouteLoaderEntry not imported in {path}"

def test_object_loader_handler_runs():
    """Repo test: object-form loader with handler runs successfully."""
    result = run_nx_test("tests/load.test.ts -t \"supports object-form loader handler\"")
    assert result.returncode == 0, f"Object-form loader test failed:\n{result.stderr[-500:]}"

def test_background_stale_reload_default():
    """Repo test: stale loaders reload in background by default."""
    result = run_nx_test("tests/load.test.ts -t \"reloads stale loaders in the background by default\"")
    assert result.returncode == 0, f"Background stale reload test failed:\n{result.stderr[-500:]}"

def test_blocking_stale_reload_loader_level():
    """Repo test: loader-level staleReloadMode blocking works."""
    result = run_nx_test("tests/load.test.ts -t \"blocks stale reloads when loader staleReloadMode is blocking\"")
    assert result.returncode == 0, f"Loader-level blocking test failed:\n{result.stderr[-500:]}"

def test_blocking_stale_reload_router_default():
    """Repo test: router defaultStaleReloadMode blocking works."""
    result = run_nx_test("tests/load.test.ts -t \"blocks stale reloads when defaultStaleReloadMode is blocking\"")
    assert result.returncode == 0, f"Router default blocking test failed:\n{result.stderr[-500:]}"

def test_loader_overrides_router_default():
    """Repo test: loader staleReloadMode overrides router default."""
    result = run_nx_test("tests/load.test.ts -t \"loader staleReloadMode overrides defaultStaleReloadMode\"")
    assert result.returncode == 0, f"Loader override test failed:\n{result.stderr[-500:]}"

def test_typescript_compiles():
    """TypeScript compilation passes for router-core."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"TypeScript type check failed:\n{result.stderr[-500:]}"

def test_unit_tests_pass():
    """All router-core unit tests pass."""
    result = run_nx_test(timeout=300)
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"

def test_repo_eslint():
    """Repo ESLint passes for router-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"

def test_repo_build_validation():
    """Repo build validation (publint/attw) passes for router-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build validation failed:\n{result.stderr[-500:]}"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
