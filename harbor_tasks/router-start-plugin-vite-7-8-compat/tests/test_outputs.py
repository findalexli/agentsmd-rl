"""Tests for TanStack Router PR #6985 - Vite 7/8 bundler options compatibility fix."""

import subprocess
import sys
import os

REPO = "/workspace/router"
PACKAGE_DIR = f"{REPO}/packages/start-plugin-core"
SRC_DIR = f"{PACKAGE_DIR}/src"


def test_bundler_options_key_removed():
    """FAIL-TO-PASS: bundlerOptionsKey export should be removed from utils.ts."""
    with open(f"{SRC_DIR}/utils.ts", "r") as f:
        content = f.read()

    # The buggy code exported bundlerOptionsKey
    assert "export const bundlerOptionsKey" not in content, \
        "bundlerOptionsKey export should be removed from utils.ts"

    # The buggy code had isRolldown detection
    assert "export const isRolldown" not in content, \
        "isRolldown export should be removed from utils.ts"

    # The buggy code checked 'rolldownVersion' in vite
    assert "'rolldownVersion' in vite" not in content, \
        "Vite version detection logic should be removed"

    # getBundlerOptions should still exist
    assert "export function getBundlerOptions" in content, \
        "getBundlerOptions function should still exist"


def test_plugin_imports_correct_utils():
    """FAIL-TO-PASS: plugin.ts should only import getBundlerOptions, not bundlerOptionsKey."""
    with open(f"{SRC_DIR}/plugin.ts", "r") as f:
        content = f.read()

    # Should not import bundlerOptionsKey
    assert "bundlerOptionsKey" not in content, \
        "plugin.ts should not reference bundlerOptionsKey"

    # Should import getBundlerOptions
    assert "import { getBundlerOptions } from './utils'" in content or \
           "import {getBundlerOptions} from './utils'" in content or \
           "getBundlerOptions" in content, \
        "plugin.ts should import or use getBundlerOptions"


def test_plugin_sets_both_bundler_options():
    """FAIL-TO-PASS: plugin.ts should set both rollupOptions and rolldownOptions for client environment."""
    with open(f"{SRC_DIR}/plugin.ts", "r") as f:
        content = f.read()

    # Should set both rollupOptions and rolldownOptions
    assert "rollupOptions: bundlerOptions" in content, \
        "plugin.ts should set rollupOptions for client environment"
    assert "rolldownOptions: bundlerOptions" in content, \
        "plugin.ts should set rolldownOptions for client environment"


def test_plugin_sets_both_bundler_options_for_server():
    """FAIL-TO-PASS: plugin.ts should set both rollupOptions and rolldownOptions for server environment."""
    with open(f"{SRC_DIR}/plugin.ts", "r") as f:
        content = f.read()

    # Count occurrences - should have at least 2 sets (client and server)
    rollup_count = content.count("rollupOptions: bundlerOptions")
    rolldown_count = content.count("rolldownOptions: bundlerOptions")

    assert rollup_count >= 2, \
        f"plugin.ts should set rollupOptions for both client and server environments (found {rollup_count})"
    assert rolldown_count >= 2, \
        f"plugin.ts should set rolldownOptions for both client and server environments (found {rolldown_count})"


def test_same_object_reference_used():
    """FAIL-TO-PASS: Both options should use same object reference to avoid Vite 8 deprecation warning."""
    with open(f"{SRC_DIR}/plugin.ts", "r") as f:
        content = f.read()

    # Check for IIFE pattern that creates shared bundlerOptions object
    assert "const bundlerOptions = {" in content, \
        "Should create a bundlerOptions object to share between rollupOptions and rolldownOptions"


def test_typescript_compiles():
    """PASS-TO-PASS: TypeScript should compile without errors."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"TypeScript type check failed:\n{result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout}\n{result.stderr[-500:] if len(result.stderr) > 500 else result.stderr}"


def test_package_builds():
    """PASS-TO-PASS: Package should build successfully."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}

    )

    assert result.returncode == 0, \
        f"Package build failed:\n{result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout}\n{result.stderr[-500:] if len(result.stderr) > 500 else result.stderr}"


def test_eslint_passes():
    """PASS-TO-PASS: ESLint should pass on the modified files."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"ESLint check failed:\n{result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout}\n{result.stderr[-500:] if len(result.stderr) > 500 else result.stderr}"


def test_unit_tests_pass():
    """PASS-TO-PASS: Unit tests for the package should pass."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # Some repos allow tests to fail if no tests exist, so we check for actual failures
    if result.returncode != 0:
        output = result.stdout + result.stderr
        # If no tests found, that's acceptable
        if "No test files found" in output or "no tests" in output.lower():
            return
        assert False, f"Unit tests failed:\n{output[-1000:]}"


def test_build_output_valid():
    """PASS-TO-PASS: Package build output passes publint and attw checks."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Build output validation failed:\n{result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout}\n{result.stderr[-500:] if len(result.stderr) > 500 else result.stderr}"
