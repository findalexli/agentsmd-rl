"""Test outputs for TanStack Router PR #6887.

This PR refactors the vue-router Link component to let buildLocation handle
the 'from' default, matching solid & react implementations. It removes the
lastMatchId and lastMatchRouteFullPath stores.
"""

import subprocess
import sys

REPO = "/workspace/router"


def run_command(cmd, cwd=REPO, timeout=300):
    """Run a shell command and return result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


# =============================================================================
# Structural Tests (Fail-to-pass)
# =============================================================================

def test_last_match_id_removed_from_stores_ts():
    """lastMatchId store should be removed from stores.ts."""
    with open(f"{REPO}/packages/router-core/src/stores.ts", 'r') as f:
        content = f.read()

    # Should NOT contain lastMatchId in the interface
    assert "lastMatchId:" not in content, "lastMatchId should be removed from stores interface"


def test_last_import_removed_from_stores_ts():
    """'last' import should be removed from stores.ts since it's no longer used there."""
    with open(f"{REPO}/packages/router-core/src/stores.ts", 'r') as f:
        content = f.read()

    # Import line should only import arraysEqual, not last
    import_line = content[content.find("import {"):content.find("} from './utils'") + len("} from './utils'")]
    assert "last" not in import_line, "last should be removed from imports in stores.ts"


def test_last_match_route_full_path_removed():
    """lastMatchRouteFullPath should be removed from vue-router routerStores.ts."""
    with open(f"{REPO}/packages/vue-router/src/routerStores.ts", 'r') as f:
        content = f.read()

    assert "lastMatchRouteFullPath" not in content, "lastMatchRouteFullPath should be removed"


def test_router_ts_uses_last_on_matches_id():
    """router.ts should use last(this.stores.matchesId.state) instead of this.stores.lastMatchId.state."""
    with open(f"{REPO}/packages/router-core/src/router.ts", 'r') as f:
        content = f.read()

    # Should use the new pattern
    assert "last(this.stores.matchesId.state)" in content, \
        "router.ts should use last(this.stores.matchesId.state)"

    # Should NOT use the old pattern
    assert "this.stores.lastMatchId.state" not in content, \
        "router.ts should not use this.stores.lastMatchId.state"


def test_vue_link_no_manual_from_computed():
    """vue-router link.tsx should not manually compute 'from' via computed."""
    with open(f"{REPO}/packages/vue-router/src/link.tsx", 'r') as f:
        content = f.read()

    # The old code had these patterns that should be removed
    assert "router.stores.lastMatchRouteFullPath" not in content, \
        "Should not reference lastMatchRouteFullPath in link.tsx"

    # Should not have the _options computed that wraps options with from
    assert "const _options = Vue.computed" not in content, \
        "Should not have _options computed wrapper"


def test_vue_link_uses_options_directly():
    """vue-router link.tsx should pass options directly to buildLocation."""
    with open(f"{REPO}/packages/vue-router/src/link.tsx", 'r') as f:
        content = f.read()

    # In SSR section, should call buildLocation(options) not buildLocation({ ...options, from })
    ssr_section = content[content.find("if (isServer ?? router.isServer)"):content.find("// Render an anchor element")]
    assert "router.buildLocation(options as any)" in ssr_section, \
        "SSR section should call buildLocation with options directly"

    # In client section, should use ...options not ..._options.value
    assert "..._options.value" not in content, \
        "Should not spread _options.value, use ...options directly"


# =============================================================================
# Repo CI/CD Tests (Pass-to-pass)
# =============================================================================

def test_router_core_typescript_types():
    """router-core TypeScript types should compile."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"router-core type check failed:\n{result.stderr[-1000:]}"


def test_vue_router_typescript_types():
    """vue-router TypeScript types should compile."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"vue-router type check failed:\n{result.stderr[-1000:]}"


def test_router_core_build():
    """router-core should build successfully."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/router-core:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"router-core build failed:\n{result.stderr[-1000:]}"


def test_vue_router_build():
    """vue-router should build successfully."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/vue-router:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"vue-router build failed:\n{result.stderr[-1000:]}"


def test_router_core_unit_tests():
    """router-core unit tests should pass (pass_to_pass)."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit",
         "--run", "--outputStyle=stream", "--skipRemoteCache"],
        timeout=300
    )
    assert result.returncode == 0, f"router-core unit tests failed:\n{result.stderr[-1000:]}"


def test_vue_router_unit_tests():
    """vue-router unit tests should pass (pass_to_pass)."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:unit",
         "--run", "--outputStyle=stream", "--skipRemoteCache"],
        timeout=300
    )
    assert result.returncode == 0, f"vue-router unit tests failed:\n{result.stderr[-1000:]}"


def test_router_core_lint():
    """router-core ESLint checks should pass (pass_to_pass)."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"router-core ESLint failed:\n{result.stderr[-1000:]}"


def test_vue_router_lint():
    """vue-router ESLint checks should pass (pass_to_pass)."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"vue-router ESLint failed:\n{result.stderr[-1000:]}"


def test_router_core_build_check():
    """router-core package build validation should pass (pass_to_pass)."""
    result = run_command(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        timeout=120
    )
    assert result.returncode == 0, f"router-core build check failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    # Run with pytest
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
