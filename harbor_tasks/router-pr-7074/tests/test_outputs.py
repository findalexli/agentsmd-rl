"""
Tests for TanStack Router HMR data initialization fix (PR #7074).

The fix adds `import.meta.hot.data ??= {}` before storing stable split components
to prevent crashes when import.meta.hot exists but import.meta.hot.data is undefined.
"""

import subprocess
import os
import re

REPO = "/workspace/router"
TARGET_FILE = "packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts"


def test_hmr_data_initialization_in_template():
    """
    fail_to_pass: Template must include import.meta.hot.data initialization.

    The buildStableSplitComponentStatements template must initialize
    import.meta.hot.data before assigning to it.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # The template must contain the initialization line
    assert "import.meta.hot.data ??= {}" in content, (
        f"Missing HMR data initialization in template.\n"
        f"Expected 'import.meta.hot.data ??= {{}}' to be present in:\n"
        f"{TARGET_FILE}"
    )


def test_initialization_inside_if_block():
    """
    fail_to_pass: Initialization must be inside the if (import.meta.hot) block.

    The initialization should occur after checking import.meta.hot exists,
    and before assigning to import.meta.hot.data[key].
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the template string in buildStableSplitComponentStatements
    # The pattern should be: if (import.meta.hot) { import.meta.hot.data ??= {}; ... }
    template_pattern = r'if\s*\(import\.meta\.hot\)\s*\{\s*import\.meta\.hot\.data\s*\?\?=\s*\{\}'

    match = re.search(template_pattern, content)
    assert match is not None, (
        f"HMR data initialization not found in correct location.\n"
        f"Expected pattern: if (import.meta.hot) {{ import.meta.hot.data ??= {{}} ...\n"
        f"File: {TARGET_FILE}"
    )


def test_router_plugin_unit_tests():
    """
    pass_to_pass: The router-plugin package unit tests must pass.

    This runs the existing test suite to ensure no regressions.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # Check for test success
    assert result.returncode == 0, (
        f"router-plugin unit tests failed:\n"
        f"stdout:\n{result.stdout[-3000:]}\n"
        f"stderr:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_type_check():
    """
    pass_to_pass: TypeScript type checking must pass for router-plugin.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Type check failed:\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_build():
    """
    pass_to_pass: The router-plugin package must build successfully.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build failed:\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_eslint():
    """
    pass_to_pass: ESLint must pass for router-plugin source code.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"ESLint failed:\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-1000:]}"
    )


def test_router_plugin_publint():
    """
    pass_to_pass: Package publishing validation (publint + attw) must pass.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Publint/ATTW validation failed:\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-1000:]}"
    )
