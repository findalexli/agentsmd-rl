"""
Tests for TanStack Router PR #6955: Vite 7/8 bundler options compatibility.

This PR adds runtime detection to support both Vite 7 (rollupOptions) and
Vite 8 (rolldownOptions) configurations.
"""

import subprocess
import os
import json

REPO = "/workspace/tanstack-router"
PACKAGE_DIR = os.path.join(REPO, "packages/start-plugin-core")
SRC_DIR = os.path.join(PACKAGE_DIR, "src")


class TestBundlerDetectionUtilities:
    """Tests for the new bundler detection utilities (fail_to_pass)."""

    def test_isRolldown_export_exists(self):
        """Verify isRolldown constant is exported from utils.ts (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The fix must export isRolldown as a const
        assert "export const isRolldown" in content, \
            "utils.ts must export 'isRolldown' constant for Vite version detection"

    def test_bundlerOptionsKey_export_exists(self):
        """Verify bundlerOptionsKey constant is exported from utils.ts (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The fix must export bundlerOptionsKey
        assert "export const bundlerOptionsKey" in content, \
            "utils.ts must export 'bundlerOptionsKey' constant"

        # It should use isRolldown to determine the value
        assert "rolldownOptions" in content and "rollupOptions" in content, \
            "bundlerOptionsKey must choose between 'rolldownOptions' and 'rollupOptions'"

    def test_getBundlerOptions_function_exists(self):
        """Verify getBundlerOptions function is exported from utils.ts (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The fix must export getBundlerOptions function
        assert "export function getBundlerOptions" in content, \
            "utils.ts must export 'getBundlerOptions' function"

    def test_getBundlerOptions_handles_both_options(self):
        """Verify getBundlerOptions reads from both rolldownOptions and rollupOptions (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The function should check rolldownOptions first, then fallback to rollupOptions
        # Look for the nullish coalescing pattern
        assert "rolldownOptions" in content, \
            "getBundlerOptions must check rolldownOptions"
        assert "rollupOptions" in content, \
            "getBundlerOptions must check rollupOptions"

        # Should use optional chaining or nullish coalescing
        assert "?." in content or "??" in content, \
            "getBundlerOptions should use optional chaining or nullish coalescing"

    def test_vite_import_for_detection(self):
        """Verify utils.ts imports vite module for version detection (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The fix imports vite to check for rolldownVersion
        assert "import * as vite from 'vite'" in content or "import vite from 'vite'" in content, \
            "utils.ts must import vite module for version detection"

    def test_rolldownVersion_detection(self):
        """Verify the detection checks for 'rolldownVersion' in vite module (fail_to_pass)."""
        utils_path = os.path.join(SRC_DIR, "utils.ts")
        with open(utils_path, "r") as f:
            content = f.read()

        # The detection should check for rolldownVersion property
        assert "rolldownVersion" in content, \
            "isRolldown detection must check for 'rolldownVersion' in vite module"


class TestPluginIntegration:
    """Tests for plugin.ts integration with new utilities (fail_to_pass)."""

    def test_plugin_imports_bundler_utilities(self):
        """Verify plugin.ts imports the new bundler utilities (fail_to_pass)."""
        plugin_path = os.path.join(SRC_DIR, "plugin.ts")
        with open(plugin_path, "r") as f:
            content = f.read()

        # The fix imports bundlerOptionsKey and getBundlerOptions from utils
        assert "bundlerOptionsKey" in content, \
            "plugin.ts must import bundlerOptionsKey from utils"
        assert "getBundlerOptions" in content, \
            "plugin.ts must import getBundlerOptions from utils"

    def test_plugin_uses_dynamic_bundler_key(self):
        """Verify plugin.ts uses dynamic bundler options key (fail_to_pass)."""
        plugin_path = os.path.join(SRC_DIR, "plugin.ts")
        with open(plugin_path, "r") as f:
            content = f.read()

        # The fix should use [bundlerOptionsKey] as computed property
        assert "[bundlerOptionsKey]" in content, \
            "plugin.ts must use [bundlerOptionsKey] as computed property instead of hardcoded 'rollupOptions'"


class TestPreviewServerPluginIntegration:
    """Tests for preview-server-plugin integration (fail_to_pass)."""

    def test_preview_plugin_imports_getBundlerOptions(self):
        """Verify preview-server-plugin imports getBundlerOptions (fail_to_pass)."""
        plugin_path = os.path.join(SRC_DIR, "preview-server-plugin/plugin.ts")
        with open(plugin_path, "r") as f:
            content = f.read()

        # The fix imports getBundlerOptions
        assert "getBundlerOptions" in content, \
            "preview-server-plugin must import getBundlerOptions from utils"

    def test_preview_plugin_uses_getBundlerOptions(self):
        """Verify preview-server-plugin uses getBundlerOptions for input access (fail_to_pass)."""
        plugin_path = os.path.join(SRC_DIR, "preview-server-plugin/plugin.ts")
        with open(plugin_path, "r") as f:
            content = f.read()

        # The fix should call getBundlerOptions to access the input
        assert "getBundlerOptions(" in content, \
            "preview-server-plugin must call getBundlerOptions() to access bundler options"


class TestPackageBuildAndQuality:
    """Pass-to-pass tests verifying existing functionality still works."""

    def test_typescript_compilation(self):
        """Verify the package compiles without TypeScript errors (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, \
            f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"

    def test_package_builds(self):
        """Verify the package builds successfully (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, \
            f"Package build failed:\n{result.stdout}\n{result.stderr}"

    def test_eslint_passes(self):
        """Verify ESLint passes on the package (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, \
            f"ESLint check failed:\n{result.stdout}\n{result.stderr}"

    def test_unit_tests(self):
        """Verify the package's vitest unit tests pass (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, \
            f"Unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

    def test_build_validation(self):
        """Verify publint and attw package validation passes (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:build"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, \
            f"Build validation failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
