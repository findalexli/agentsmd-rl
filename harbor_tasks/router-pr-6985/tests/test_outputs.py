"""
Benchmark tests for TanStack/router PR #6985:
Fix Vite 7/8 bundler options compatibility in start-plugin-core.

The bug: The plugin used dynamic detection (`isRolldown`) to choose between
`rollupOptions` and `rolldownOptions`, but in pnpm workspaces, the detection
could resolve the wrong Vite version, causing builds to fail.

The fix: Set both `rollupOptions` and `rolldownOptions` simultaneously.
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/router")
PLUGIN_SRC = REPO / "packages/start-plugin-core/src"


def test_bundlerOptionsKey_removed_from_utils():
    """
    The bundlerOptionsKey export should be removed from utils.ts.

    The fix removes the dynamic key selection since both keys are now set.
    This test fails on the base commit (where bundlerOptionsKey exists)
    and passes after the fix (where it's removed).
    """
    utils_path = PLUGIN_SRC / "utils.ts"
    content = utils_path.read_text()

    # bundlerOptionsKey should NOT be exported
    assert "export const bundlerOptionsKey" not in content, (
        "bundlerOptionsKey should be removed - the fix sets both rollupOptions "
        "and rolldownOptions directly instead of using dynamic key selection"
    )


def test_isRolldown_removed_from_utils():
    """
    The isRolldown constant should be removed from utils.ts.

    The fix eliminates version detection logic since it was unreliable
    in pnpm workspaces.
    """
    utils_path = PLUGIN_SRC / "utils.ts"
    content = utils_path.read_text()

    # isRolldown should NOT be exported
    assert "export const isRolldown" not in content, (
        "isRolldown constant should be removed - version detection is no longer needed"
    )


def test_plugin_imports_updated():
    """
    plugin.ts should not import bundlerOptionsKey since it's removed.
    """
    plugin_path = PLUGIN_SRC / "plugin.ts"
    content = plugin_path.read_text()

    # Should NOT import bundlerOptionsKey
    assert "bundlerOptionsKey" not in content, (
        "plugin.ts should not reference bundlerOptionsKey after the fix"
    )


def test_plugin_sets_both_rollup_and_rolldown_options():
    """
    plugin.ts should set both rollupOptions and rolldownOptions.

    This is the core behavioral fix: both keys should be present
    so both Vite 7 (rollupOptions) and Vite 8 (rolldownOptions) work.
    """
    plugin_path = PLUGIN_SRC / "plugin.ts"
    content = plugin_path.read_text()

    # Should have rollupOptions: bundlerOptions
    assert "rollupOptions: bundlerOptions" in content or "rollupOptions:" in content, (
        "plugin.ts should set rollupOptions for Vite 7 compatibility"
    )

    # Should have rolldownOptions: bundlerOptions
    assert "rolldownOptions: bundlerOptions" in content or "rolldownOptions:" in content, (
        "plugin.ts should set rolldownOptions for Vite 8 compatibility"
    )


def test_utils_no_vite_import():
    """
    utils.ts should not import vite since version detection is removed.
    """
    utils_path = PLUGIN_SRC / "utils.ts"
    content = utils_path.read_text()

    # Should NOT import vite
    assert "import * as vite from 'vite'" not in content, (
        "utils.ts should not import vite since isRolldown detection is removed"
    )


def test_typescript_compiles():
    """
    The package should compile without TypeScript errors (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={"CI": "1", "NX_DAEMON": "false", **__import__("os").environ}
    )
    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stderr[-2000:]}"
    )


def test_eslint_passes():
    """
    ESLint should pass on the start-plugin-core package (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={"CI": "1", "NX_DAEMON": "false", **__import__("os").environ}
    )
    assert result.returncode == 0, (
        f"ESLint failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
    )


def test_repo_unit_tests():
    """
    Repo's unit tests pass for start-plugin-core (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={"CI": "1", "NX_DAEMON": "false", **__import__("os").environ}
    )
    assert result.returncode == 0, (
        f"Unit tests failed:\n{result.stderr[-1500:]}\n{result.stdout[-500:]}"
    )


def test_repo_types():
    """
    TypeScript type checking passes (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types:ts59"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={"CI": "1", "NX_DAEMON": "false", **__import__("os").environ}
    )
    assert result.returncode == 0, (
        f"Type checking failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"
    )


def test_repo_build_quality():
    """
    Package build quality checks pass (publint, attw) (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={"CI": "1", "NX_DAEMON": "false", **__import__("os").environ}
    )
    assert result.returncode == 0, (
        f"Build quality checks failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"
    )


def test_client_env_has_dual_bundler_options():
    """
    The client environment config should have both rollupOptions and rolldownOptions.

    This ensures Vite 7 (which reads rollupOptions) and Vite 8 (which reads
    rolldownOptions) both receive the correct bundler configuration.
    """
    plugin_path = PLUGIN_SRC / "plugin.ts"
    content = plugin_path.read_text()

    # Find the client environment block
    # The client environment should have both options set

    # Look for the pattern where bundlerOptions is created and both are set
    has_bundler_options_pattern = bool(re.search(
        r"const bundlerOptions\s*=\s*\{[^}]*input:\s*\{\s*main:\s*ENTRY_POINTS\.client",
        content,
        re.DOTALL
    ))

    has_rollup = "rollupOptions: bundlerOptions" in content
    has_rolldown = "rolldownOptions: bundlerOptions" in content

    assert has_bundler_options_pattern or (has_rollup and has_rolldown), (
        "Client environment should define bundlerOptions and assign it to both "
        "rollupOptions and rolldownOptions"
    )


def test_server_env_has_dual_bundler_options():
    """
    The server environment config should have both rollupOptions and rolldownOptions.
    """
    plugin_path = PLUGIN_SRC / "plugin.ts"
    content = plugin_path.read_text()

    # Look for server entry point with bundlerOptions pattern
    has_server_bundler_options = bool(re.search(
        r"const bundlerOptions\s*=\s*\{[^}]*input:\s*\{\s*main:\s*ENTRY_POINTS\.server",
        content,
        re.DOTALL
    ))

    # Count occurrences of the dual assignment pattern
    rollup_count = content.count("rollupOptions: bundlerOptions")
    rolldown_count = content.count("rolldownOptions: bundlerOptions")

    # Should have at least 2 of each (one for client, one for server)
    assert (has_server_bundler_options or (rollup_count >= 2 and rolldown_count >= 2)), (
        "Server environment should also use dual bundler options pattern"
    )
