"""
Test suite for TanStack Router PR #6919: Hoist inline component definitions for proper React HMR.

This PR adds:
1. getUniqueProgramIdentifier utility function to generate collision-free identifiers
2. A plugin system for route compilation
3. createReactRefreshRouteComponentsPlugin that hoists inline component definitions
"""

import subprocess
import os
import sys

REPO = "/workspace/router"
PLUGIN_PKG = os.path.join(REPO, "packages/router-plugin")


def test_get_unique_program_identifier_function_exists():
    """The getUniqueProgramIdentifier function must be exported from utils.ts (fail_to_pass)."""
    utils_path = os.path.join(PLUGIN_PKG, "src/core/utils.ts")
    with open(utils_path, "r") as f:
        content = f.read()

    # Check that the function is defined and exported
    assert "export function getUniqueProgramIdentifier" in content, \
        "getUniqueProgramIdentifier function must be exported from utils.ts"

    # Check function signature includes required parameters
    assert "programPath:" in content and "baseName:" in content, \
        "Function must accept programPath and baseName parameters"


def test_get_unique_program_identifier_handles_collisions():
    """The getUniqueProgramIdentifier must increment suffix to avoid naming collisions (fail_to_pass)."""
    utils_path = os.path.join(PLUGIN_PKG, "src/core/utils.ts")
    with open(utils_path, "r") as f:
        content = f.read()

    # Check that the function handles name collisions by incrementing a suffix
    assert "suffix" in content, \
        "Function must use a suffix counter for collision avoidance"
    assert "hasBinding" in content or "hasGlobal" in content, \
        "Function must check for existing bindings/globals"
    assert "while" in content, \
        "Function must loop until a unique name is found"


def test_plugins_types_file_exists():
    """The plugins.ts file must define the plugin interface types (fail_to_pass)."""
    plugins_path = os.path.join(PLUGIN_PKG, "src/core/code-splitter/plugins.ts")
    assert os.path.exists(plugins_path), \
        f"plugins.ts must exist at {plugins_path}"

    with open(plugins_path, "r") as f:
        content = f.read()

    # Check for required type definitions
    assert "ReferenceRouteCompilerPlugin" in content, \
        "plugins.ts must define ReferenceRouteCompilerPlugin type"
    assert "ReferenceRouteCompilerPluginContext" in content, \
        "plugins.ts must define ReferenceRouteCompilerPluginContext type"
    assert "onUnsplittableRoute" in content, \
        "Plugin interface must define onUnsplittableRoute hook"


def test_react_refresh_plugin_exists():
    """The react-refresh-route-components.ts plugin must exist (fail_to_pass)."""
    plugin_path = os.path.join(
        PLUGIN_PKG, "src/core/code-splitter/plugins/react-refresh-route-components.ts"
    )
    assert os.path.exists(plugin_path), \
        f"react-refresh-route-components.ts must exist at {plugin_path}"

    with open(plugin_path, "r") as f:
        content = f.read()

    assert "createReactRefreshRouteComponentsPlugin" in content, \
        "Plugin must export createReactRefreshRouteComponentsPlugin function"


def test_react_refresh_plugin_hoists_component_identifiers():
    """The react-refresh plugin must hoist component, pendingComponent, errorComponent, notFoundComponent (fail_to_pass)."""
    plugin_path = os.path.join(
        PLUGIN_PKG, "src/core/code-splitter/plugins/react-refresh-route-components.ts"
    )
    with open(plugin_path, "r") as f:
        content = f.read()

    # Verify the plugin handles all route component identifiers
    required_idents = ["component", "pendingComponent", "errorComponent", "notFoundComponent"]
    for ident in required_idents:
        assert ident in content, \
            f"Plugin must handle '{ident}' route option"

    # Verify it creates hoisted declarations
    assert "hoistedDeclarations" in content or "variableDeclaration" in content, \
        "Plugin must create hoisted variable declarations"

    # Verify it uses getUniqueProgramIdentifier
    assert "getUniqueProgramIdentifier" in content, \
        "Plugin must use getUniqueProgramIdentifier for collision-free naming"


def test_framework_plugins_returns_react_plugin():
    """getReferenceRouteCompilerPlugins returns react-refresh plugin for React target with HMR (fail_to_pass)."""
    plugins_path = os.path.join(
        PLUGIN_PKG, "src/core/code-splitter/plugins/framework-plugins.ts"
    )
    assert os.path.exists(plugins_path), \
        f"framework-plugins.ts must exist at {plugins_path}"

    with open(plugins_path, "r") as f:
        content = f.read()

    assert "getReferenceRouteCompilerPlugins" in content, \
        "Must export getReferenceRouteCompilerPlugins function"
    assert "react" in content.lower(), \
        "Function must handle 'react' target framework"
    assert "createReactRefreshRouteComponentsPlugin" in content, \
        "Function must return createReactRefreshRouteComponentsPlugin for React"


def test_compilers_accepts_compiler_plugins():
    """compileCodeSplitReferenceRoute must accept compilerPlugins option (fail_to_pass)."""
    compilers_path = os.path.join(PLUGIN_PKG, "src/core/code-splitter/compilers.ts")
    with open(compilers_path, "r") as f:
        content = f.read()

    assert "compilerPlugins" in content, \
        "compileCodeSplitReferenceRoute must accept compilerPlugins option"
    assert "ReferenceRouteCompilerPlugin" in content, \
        "compilers.ts must import ReferenceRouteCompilerPlugin type"


def test_router_code_splitter_uses_plugins():
    """router-code-splitter-plugin must use getReferenceRouteCompilerPlugins (fail_to_pass)."""
    plugin_path = os.path.join(PLUGIN_PKG, "src/core/router-code-splitter-plugin.ts")
    with open(plugin_path, "r") as f:
        content = f.read()

    assert "getReferenceRouteCompilerPlugins" in content, \
        "router-code-splitter-plugin must use getReferenceRouteCompilerPlugins"
    assert "compilerPlugins" in content, \
        "router-code-splitter-plugin must pass compilerPlugins to compiler"


def test_router_hmr_plugin_uses_plugins():
    """router-hmr-plugin must use getReferenceRouteCompilerPlugins for React target (fail_to_pass)."""
    plugin_path = os.path.join(PLUGIN_PKG, "src/core/router-hmr-plugin.ts")
    with open(plugin_path, "r") as f:
        content = f.read()

    assert "getReferenceRouteCompilerPlugins" in content, \
        "router-hmr-plugin must use getReferenceRouteCompilerPlugins"
    assert "compileCodeSplitReferenceRoute" in content, \
        "router-hmr-plugin must use compileCodeSplitReferenceRoute for React"


def test_repo_plugin_eslint():
    """The router-plugin ESLint check must pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"router-plugin ESLint failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_plugin_build():
    """The router-plugin package must build successfully (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"router-plugin build failed:\n{result.stderr[-2000:]}"


def test_repo_plugin_build_validation():
    """The router-plugin build validation (publint + attw) must pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"router-plugin build validation failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_plugin_unit_tests():
    """The router-plugin unit tests must pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"router-plugin unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_plugin_type_check():
    """The router-plugin type check must pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"router-plugin type check failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
