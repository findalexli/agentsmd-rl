"""Tests for router HMR data initialization fix."""

import subprocess
import sys
import os

REPO = "/workspace/router"
TARGET_FILE = "packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts"
FULL_TARGET_PATH = f"{REPO}/{TARGET_FILE}"


def test_source_code_initializes_hot_data():
    """
    F2P: Source code must initialize import.meta.hot.data before storing to it.

    The fix adds `import.meta.hot.data ??= {}` before accessing properties
    on import.meta.hot.data to prevent Vitest crashes when HMR data is missing.

    This is the primary test - the source code transformation template must
    include the initialization.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check that the initialization line exists
    assert "import.meta.hot.data ??= {}" in content, (
        "Missing required initialization: `import.meta.hot.data ??= {}`\n"
        f"File content:\n{content}"
    )

    # Check that the initialization happens BEFORE the data access
    # The pattern should be: first `??= {}`, then `.data[...] =`
    lines = content.split('\n')
    init_line_idx = None
    data_access_idx = None

    for i, line in enumerate(lines):
        if "import.meta.hot.data ??= {}" in line:
            init_line_idx = i
        if "import.meta.hot.data[%%hotDataKey%%]" in line and data_access_idx is None:
            data_access_idx = i

    assert init_line_idx is not None, "Initialization line not found"
    assert data_access_idx is not None, "Data access pattern not found"
    assert init_line_idx < data_access_idx, (
        f"Initialization must come BEFORE data access. "
        f"Init at line {init_line_idx}, access at line {data_access_idx}"
    )


def test_source_has_correct_template_structure():
    """
    F2P: The template must have correct structure for HMR handling.

    The template should generate code that:
    1. Reads from import.meta.hot?.data?.[key]
    2. Initializes import.meta.hot.data ??= {}
    3. Writes back to import.meta.hot.data[key]
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check template has the hot data read pattern
    assert "import.meta.hot?.data?.[%%hotDataKey%%]" in content, (
        "Template must read from import.meta.hot.data with optional chaining"
    )

    # Check template has the assignment pattern
    assert "import.meta.hot.data[%%hotDataKey%%]" in content, (
        "Template must write to import.meta.hot.data[key]"
    )

    # Check the template is in the buildStableSplitComponentStatements
    assert "buildStableSplitComponentStatements" in content, (
        "File must contain buildStableSplitComponentStatements template"
    )


def test_hmr_test_file_exists():
    """
    P2P: HMR test file should exist and be testable.
    """
    test_file = f"{REPO}/packages/router-plugin/tests/add-hmr.test.ts"
    assert os.path.exists(test_file), f"Test file not found: {test_file}"


def test_router_plugin_build():
    """
    P2P: Router plugin package should build successfully.

    After the source change, the package must still compile.
    """
    result = subprocess.run(
        ["CI=1", "NX_DAEMON=false", "pnpm", "nx", "run", "@tanstack/router-plugin:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        shell=True
    )

    assert result.returncode == 0, (
        f"Router plugin build failed:\n"
        f"STDOUT:\n{result.stdout[-1000:]}\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_unit_tests():
    """
    P2P: Router plugin unit tests should pass.

    This uses the repo's own test suite to verify the fix doesn't break anything.
    The test suite includes tests that check for the correct HMR output.
    """
    result = subprocess.run(
        ["CI=1", "NX_DAEMON=false", "pnpm", "nx", "run", "@tanstack/router-plugin:test:unit", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        shell=True
    )

    assert result.returncode == 0, (
        f"Router plugin unit tests failed:\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )


def test_router_plugin_lint():
    """
    P2P: Router plugin ESLint checks should pass.

    This uses the repo's own linting setup to verify the fix follows
    the project's coding standards.
    """
    result = subprocess.run(
        ["CI=1", "NX_DAEMON=false", "pnpm", "nx", "run", "@tanstack/router-plugin:test:eslint", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        shell=True
    )

    assert result.returncode == 0, (
        f"Router plugin lint failed:\n"
        f"STDOUT:\n{result.stdout[-1000:]}\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_types():
    """
    P2P: Router plugin TypeScript type checking should pass.

    This verifies the fix doesn't introduce any type errors across
    multiple TypeScript versions (5.5 through 6.0).
    """
    result = subprocess.run(
        ["CI=1", "NX_DAEMON=false", "pnpm", "nx", "run", "@tanstack/router-plugin:test:types", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        shell=True
    )

    assert result.returncode == 0, (
        f"Router plugin type check failed:\n"
        f"STDOUT:\n{result.stdout[-1000:]}\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_build_validation():
    """
    P2P: Router plugin package build validation should pass.

    This runs publint and attw to verify the package exports are
    correctly configured for all entry points (main, vite, rspack, webpack, esbuild).
    """
    result = subprocess.run(
        ["CI=1", "NX_DAEMON=false", "pnpm", "nx", "run", "@tanstack/router-plugin:test:build", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        shell=True
    )

    assert result.returncode == 0, (
        f"Router plugin build validation failed:\n"
        f"STDOUT:\n{result.stdout[-1000:]}\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )
