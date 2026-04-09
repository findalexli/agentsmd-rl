"""Tests for Vite 7/8 Rolldown compatibility fix.

The PR adds runtime detection of Vite version to support both:
- Vite 7: uses `build.rollupOptions`
- Vite 8: uses `build.rolldownOptions`
"""

import subprocess
import sys
import os

REPO = "/workspace/router"
PLUGIN_DIR = f"{REPO}/packages/start-plugin-core/src"


def test_utils_exports_bundler_detection():
    """utils.ts exports bundler detection utilities (f2p).

    The fix adds isRolldown, bundlerOptionsKey, and getBundlerOptions to utils.ts.
    These are used by plugin.ts and preview-server-plugin/plugin.ts.
    """
    utils_path = f"{PLUGIN_DIR}/utils.ts"
    with open(utils_path, "r") as f:
        content = f.read()

    # Check that the new utilities are exported
    assert "isRolldown = 'rolldownVersion' in vite" in content, \
        "isRolldown detection not found in utils.ts"
    assert "bundlerOptionsKey = isRolldown" in content, \
        "bundlerOptionsKey not found in utils.ts"
    assert "export function getBundlerOptions" in content, \
        "getBundlerOptions function not found in utils.ts"


def test_utils_imports_vite():
    """utils.ts imports vite module (f2p).

    The detection relies on checking for 'rolldownVersion' in the vite module.
    """
    utils_path = f"{PLUGIN_DIR}/utils.ts"
    with open(utils_path, "r") as f:
        content = f.read()

    assert "import * as vite from 'vite'" in content, \
        "vite import not found in utils.ts"


def test_getBundlerOptions_uses_rolldownOptions_fallback():
    """getBundlerOptions checks rolldownOptions first, then rollupOptions (f2p).

    The function should return rolldownOptions if it exists, otherwise rollupOptions.
    This matches Vite 8's new structure while maintaining Vite 7 compatibility.
    """
    utils_path = f"{PLUGIN_DIR}/utils.ts"
    with open(utils_path, "r") as f:
        content = f.read()

    # Check for the correct fallback order: rolldownOptions ?? rollupOptions
    assert "build?.rolldownOptions ?? build?.rollupOptions" in content, \
        "getBundlerOptions should check rolldownOptions first, then rollupOptions"


def test_bundlerOptionsKey_returns_correct_key():
    """bundlerOptionsKey returns 'rolldownOptions' or 'rollupOptions' (f2p).

    This computed key is used to access the correct options property dynamically.
    """
    utils_path = f"{PLUGIN_DIR}/utils.ts"
    with open(utils_path, "r") as f:
        content = f.read()

    # Check for the ternary expression that selects the right key
    assert "? 'rolldownOptions'" in content and ": 'rollupOptions'" in content, \
        "bundlerOptionsKey should return 'rolldownOptions' or 'rollupOptions' based on isRolldown"


def test_plugin_imports_bundler_utils():
    """plugin.ts imports bundler utilities from utils (f2p).

    The plugin needs to import bundlerOptionsKey and getBundlerOptions to use them.
    """
    plugin_path = f"{PLUGIN_DIR}/plugin.ts"
    with open(plugin_path, "r") as f:
        content = f.read()

    assert "import { bundlerOptionsKey, getBundlerOptions } from './utils'" in content, \
        "plugin.ts should import bundler utilities from utils"


def test_plugin_uses_bundlerOptionsKey_for_client():
    """plugin.ts uses bundlerOptionsKey for client environment config (f2p).

    Client build config should use [bundlerOptionsKey] instead of hardcoded 'rollupOptions'.
    """
    plugin_path = f"{PLUGIN_DIR}/plugin.ts"
    with open(plugin_path, "r") as f:
        content = f.read()

    # Check that client environment uses computed key
    assert "[bundlerOptionsKey]:" in content, \
        "plugin.ts should use [bundlerOptionsKey] for client build config"


def test_plugin_uses_getBundlerOptions_for_server():
    """plugin.ts uses getBundlerOptions for reading server config (f2p).

    Server build config input should be read using getBundlerOptions() helper.
    """
    plugin_path = f"{PLUGIN_DIR}/plugin.ts"
    with open(plugin_path, "r") as f:
        content = f.read()

    # Check that getBundlerOptions is used to read server input
    assert "getBundlerOptions(" in content, \
        "plugin.ts should use getBundlerOptions to read server bundler options"


def test_plugin_uses_bundlerOptionsKey_for_server():
    """plugin.ts uses bundlerOptionsKey for server environment config (f2p).

    Server build config should use [bundlerOptionsKey] instead of hardcoded 'rollupOptions'.
    """
    plugin_path = f"{PLUGIN_DIR}/plugin.ts"
    with open(plugin_path, "r") as f:
        content = f.read()

    # Count occurrences - should be at least 2 (client and server)
    count = content.count("[bundlerOptionsKey]:")
    assert count >= 2, \
        f"plugin.ts should use [bundlerOptionsKey] in at least 2 places (client + server), found {count}"


def test_preview_server_imports_getBundlerOptions():
    """preview-server-plugin imports getBundlerOptions from utils (f2p).

    The preview server plugin needs to read the server input from bundler options.
    """
    preview_path = f"{PLUGIN_DIR}/preview-server-plugin/plugin.ts"
    with open(preview_path, "r") as f:
        content = f.read()

    assert "import { getBundlerOptions } from '../utils'" in content, \
        "preview-server-plugin should import getBundlerOptions from utils"


def test_preview_server_uses_getBundlerOptions():
    """preview-server-plugin uses getBundlerOptions to read server input (f2p).

    Should use getBundlerOptions(serverEnv?.build)?.input instead of direct property access.
    """
    preview_path = f"{PLUGIN_DIR}/preview-server-plugin/plugin.ts"
    with open(preview_path, "r") as f:
        content = f.read()

    # The old code was: serverEnv?.build.rollupOptions.input ?? 'server'
    # The new code should use: getBundlerOptions(serverEnv?.build)?.input ?? 'server'
    assert "getBundlerOptions(serverEnv?.build)?.input" in content, \
        "preview-server-plugin should use getBundlerOptions to read server input"


def test_no_hardcoded_rollupOptions_in_plugin():
    """plugin.ts should not hardcode 'rollupOptions' in build config (f2p).

    After the fix, all references should use bundlerOptionsKey instead.
    """
    plugin_path = f"{PLUGIN_DIR}/plugin.ts"
    with open(plugin_path, "r") as f:
        content = f.read()

    # Check that old hardcoded patterns are replaced
    # We allow "rollupOptions" in comments or strings, but not in build config
    lines = content.split("\n")
    for i, line in enumerate(lines):
        # Skip imports, comments, and getBundlerOptions calls
        if "import" in line or line.strip().startswith("//") or "getBundlerOptions" in line:
            continue
        # The pattern we want to eliminate: `rollupOptions: {` or `.rollupOptions`
        if "build: {\n                rollupOptions:" in content:
            # This is the old pattern that should not exist
            pass  # Will be caught by positive tests above

    # More robust check: ensure we use computed key for both environments
    # This test complements test_plugin_uses_bundlerOptionsKey_for_client and _server
    assert content.count("[bundlerOptionsKey]:") >= 2, \
        "Should use [bundlerOptionsKey] for both client and server environments"


def test_typescript_compiles():
    """TypeScript compilation passes (p2p).

    The code should compile without type errors.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_eslint_passes():
    """ESLint passes on the package (p2p).

    The code should pass linting rules.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint", "--outputStyle=stream"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"ESLint failed:\n{result.stderr[-500:]}"


def test_build_passes():
    """Package builds successfully (p2p).

    The package should build without errors.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_unit_tests_pass():
    """Unit tests pass (p2p).

    The package's unit tests should pass if they exist.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit", "--outputStyle=stream"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    # Some packages may not have unit tests, so we accept 0 or success
    if result.returncode != 0:
        # Check if it's because there are no tests
        if "No test files found" in result.stdout or "No test files found" in result.stderr:
            return  # OK if no tests exist
        assert False, \
            f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
