"""
Tests for TanStack Router Vite 7/8 compatibility PR.

This tests that the start-plugin-core package correctly detects Vite version
and uses the appropriate bundler options key (rollupOptions for Vite 7,
rolldownOptions for Vite 8).
"""

import subprocess
import sys
import os

REPO = "/workspace/router"
PACKAGE = f"{REPO}/packages/start-plugin-core"


# =============================================================================
# PASS-TO-PASS TESTS (repo CI/CD checks - must pass on both base and fixed)
# =============================================================================

def test_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_types():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build check failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit", "--run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# =============================================================================
# FAIL-TO-PASS TESTS (specific to this PR)
# =============================================================================


def test_typescript_compiles():
    """Package must compile without TypeScript errors."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_utils_exports_isRolldown():
    """utils.ts must export isRolldown constant for Vite version detection."""
    utils_path = f"{PACKAGE}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Check for isRolldown export
    assert "export const isRolldown" in content, "Missing isRolldown export in utils.ts"
    assert "'rolldownVersion' in vite" in content, "isRolldown should check for 'rolldownVersion' in vite"


def test_utils_exports_bundlerOptionsKey():
    """utils.ts must export bundlerOptionsKey constant."""
    utils_path = f"{PACKAGE}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    assert "export const bundlerOptionsKey" in content, "Missing bundlerOptionsKey export in utils.ts"
    # Check conditional assignment
    assert "isRolldown" in content, "bundlerOptionsKey should reference isRolldown"


def test_utils_exports_getBundlerOptions():
    """utils.ts must export getBundlerOptions function."""
    utils_path = f"{PACKAGE}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    assert "export function getBundlerOptions" in content, "Missing getBundlerOptions export in utils.ts"
    # Check that it reads both options
    assert "rolldownOptions" in content, "getBundlerOptions should reference rolldownOptions"
    assert "rollupOptions" in content, "getBundlerOptions should reference rollupOptions"


def test_vite_import_in_utils():
    """utils.ts must import vite module for version detection."""
    utils_path = f"{PACKAGE}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    assert "import * as vite from 'vite'" in content, "Missing vite import in utils.ts"


def test_plugin_uses_bundlerOptionsKey():
    """plugin.ts must use bundlerOptionsKey instead of hardcoded 'rollupOptions'."""
    plugin_path = f"{PACKAGE}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    assert "import { bundlerOptionsKey, getBundlerOptions }" in content, \
        "plugin.ts must import bundlerOptionsKey and getBundlerOptions from utils"

    # Check that bundlerOptionsKey is used in client environment
    assert "[bundlerOptionsKey]:" in content, \
        "plugin.ts must use [bundlerOptionsKey] instead of hardcoded rollupOptions"


def test_plugin_uses_getBundlerOptions():
    """plugin.ts must use getBundlerOptions to read bundler config."""
    plugin_path = f"{PACKAGE}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    assert "getBundlerOptions(" in content, \
        "plugin.ts must use getBundlerOptions() to access bundler configuration"


def test_preview_server_uses_getBundlerOptions():
    """preview-server-plugin must use getBundlerOptions."""
    preview_path = f"{PACKAGE}/src/preview-server-plugin/plugin.ts"
    with open(preview_path, 'r') as f:
        content = f.read()

    assert "import { getBundlerOptions }" in content, \
        "preview-server-plugin/plugin.ts must import getBundlerOptions"
    assert "getBundlerOptions(serverEnv?.build)?.input" in content, \
        "preview-server-plugin must use getBundlerOptions to read server input"


def test_no_hardcoded_rollupOptions_in_plugin():
    """plugin.ts should not have hardcoded rollupOptions references in environment configs."""
    plugin_path = f"{PACKAGE}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    # After the fix, the file should use dynamic key, not hardcoded rollupOptions in build configs
    # The only rollupOptions reference should be inside getBundlerOptions or as fallback
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Skip lines that are part of getBundlerOptions function or comments
        if 'rollupOptions' in line:
            # Allow references inside getBundlerOptions or comments
            if 'getBundlerOptions' in line or '//' in line:
                continue
            # Allow the fallback pattern: build?.rollupOptions
            if 'build?.rollupOptions' in line or 'build?.rolldownOptions' in line:
                continue
            # Any other hardcoded rollupOptions is a problem
            assert False, f"Found hardcoded rollupOptions at line {i+1}: {line}"
