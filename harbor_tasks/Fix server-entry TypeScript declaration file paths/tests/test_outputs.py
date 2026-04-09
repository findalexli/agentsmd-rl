"""
Test suite for TanStack Router PR #7035

This PR fixes missing TypeScript declaration files for server-entry exports
by adding proper tsconfig.server-entry.json files with correct rootDir configuration.

The issue: With TypeScript 6, the default rootDir changed from inferred to ".",
causing vite-plugin-dts to emit declarations at the wrong path:
  - Wrong: dist/default-entry/esm/src/default-entry/server.d.ts
  - Correct: dist/default-entry/esm/server.d.ts

The fix adds tsconfig.server-entry.json files with rootDir: "./src/default-entry"
and updates vite.config.server-entry.ts to reference them.
"""

import subprocess
import os
import json
import glob

REPO = "/workspace/router"

# Package directories
REACT_START = f"{REPO}/packages/react-start"
SOLID_START = f"{REPO}/packages/solid-start"
VUE_START = f"{REPO}/packages/vue-start"


def run_command(cmd, cwd=None, timeout=120):
    """Run a shell command and return result."""
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


def test_react_start_server_dts_exists():
    """
    Verify that react-start package emits server.d.ts at correct path.

    The declaration file should exist at:
    packages/react-start/dist/default-entry/esm/server.d.ts
    """
    expected_path = f"{REACT_START}/dist/default-entry/esm/server.d.ts"

    # First, build the package
    result = run_command(["pnpm", "build"], cwd=REACT_START, timeout=180)

    # Check that the expected file exists
    assert os.path.exists(expected_path), (
        f"Expected server.d.ts at {expected_path} does not exist.\n"
        f"Build output:\n{result.stdout}\n{result.stderr}"
    )

    # Verify it's a valid declaration file
    with open(expected_path, 'r') as f:
        content = f.read()
        assert 'export' in content or 'declare' in content, (
            f"File {expected_path} does not appear to be a valid TypeScript declaration file"
        )


def test_solid_start_server_dts_exists():
    """
    Verify that solid-start package emits server.d.ts at correct path.

    The declaration file should exist at:
    packages/solid-start/dist/default-entry/esm/server.d.ts
    """
    expected_path = f"{SOLID_START}/dist/default-entry/esm/server.d.ts"

    # First, build the package
    result = run_command(["pnpm", "build"], cwd=SOLID_START, timeout=180)

    # Check that the expected file exists
    assert os.path.exists(expected_path), (
        f"Expected server.d.ts at {expected_path} does not exist.\n"
        f"Build output:\n{result.stdout}\n{result.stderr}"
    )

    # Verify it's a valid declaration file
    with open(expected_path, 'r') as f:
        content = f.read()
        assert 'export' in content or 'declare' in content, (
            f"File {expected_path} does not appear to be a valid TypeScript declaration file"
        )


def test_vue_start_server_dts_exists():
    """
    Verify that vue-start package emits server.d.ts at correct path.

    The declaration file should exist at:
    packages/vue-start/dist/default-entry/esm/server.d.ts
    """
    expected_path = f"{VUE_START}/dist/default-entry/esm/server.d.ts"

    # First, build the package
    result = run_command(["pnpm", "build"], cwd=VUE_START, timeout=180)

    # Check that the expected file exists
    assert os.path.exists(expected_path), (
        f"Expected server.d.ts at {expected_path} does not exist.\n"
        f"Build output:\n{result.stdout}\n{result.stderr}"
    )

    # Verify it's a valid declaration file
    with open(expected_path, 'r') as f:
        content = f.read()
        assert 'export' in content or 'declare' in content, (
            f"File {expected_path} does not appear to be a valid TypeScript declaration file"
        )


def test_react_start_publint_pass():
    """
    Verify that react-start package passes publint validation.

    The package should be correctly structured for npm publishing.
    """
    # Check if publint is available, install if needed
    result = run_command(["pnpm", "exec", "publint", "--version"], cwd=REACT_START)
    if result.returncode != 0:
        # Install publint if not available
        result = run_command(["pnpm", "add", "-D", "publint"], cwd=REACT_START, timeout=60)

    # Run publint with --strict flag
    result = run_command(["pnpm", "exec", "publint", "--strict", "."], cwd=REACT_START, timeout=60)

    assert result.returncode == 0, (
        f"publint failed for react-start package:\n{result.stdout}\n{result.stderr}"
    )


def test_solid_start_publint_pass():
    """
    Verify that solid-start package passes publint validation.

    The package should be correctly structured for npm publishing.
    """
    # Check if publint is available, install if needed
    result = run_command(["pnpm", "exec", "publint", "--version"], cwd=SOLID_START)
    if result.returncode != 0:
        # Install publint if not available
        result = run_command(["pnpm", "add", "-D", "publint"], cwd=SOLID_START, timeout=60)

    # Run publint with --strict flag
    result = run_command(["pnpm", "exec", "publint", "--strict", "."], cwd=SOLID_START, timeout=60)

    assert result.returncode == 0, (
        f"publint failed for solid-start package:\n{result.stdout}\n{result.stderr}"
    )


def test_vue_start_publint_pass():
    """
    Verify that vue-start package passes publint validation.

    The package should be correctly structured for npm publishing.
    """
    # Check if publint is available, install if needed
    result = run_command(["pnpm", "exec", "publint", "--version"], cwd=VUE_START)
    if result.returncode != 0:
        # Install publint if not available
        result = run_command(["pnpm", "add", "-D", "publint"], cwd=VUE_START, timeout=60)

    # Run publint with --strict flag
    result = run_command(["pnpm", "exec", "publint", "--strict", "."], cwd=VUE_START, timeout=60)

    assert result.returncode == 0, (
        f"publint failed for vue-start package:\n{result.stdout}\n{result.stderr}"
    )


def test_react_start_vite_config_has_tsconfig_path():
    """
    Verify that react-start's vite.config.server-entry.ts references tsconfig.server-entry.json.

    The vite config should have tsconfigPath: './tsconfig.server-entry.json' set.
    """
    vite_config_path = f"{REACT_START}/vite.config.server-entry.ts"

    assert os.path.exists(vite_config_path), (
        f"vite.config.server-entry.ts not found at {vite_config_path}"
    )

    with open(vite_config_path, 'r') as f:
        content = f.read()

    assert "tsconfigPath: './tsconfig.server-entry.json'" in content, (
        f"vite.config.server-entry.ts should reference tsconfig.server-entry.json\n"
        f"Content:\n{content}"
    )


def test_solid_start_vite_config_has_tsconfig_path():
    """
    Verify that solid-start's vite.config.server-entry.ts references tsconfig.server-entry.json.

    The vite config should have tsconfigPath: './tsconfig.server-entry.json' set.
    """
    vite_config_path = f"{SOLID_START}/vite.config.server-entry.ts"

    assert os.path.exists(vite_config_path), (
        f"vite.config.server-entry.ts not found at {vite_config_path}"
    )

    with open(vite_config_path, 'r') as f:
        content = f.read()

    assert "tsconfigPath: './tsconfig.server-entry.json'" in content, (
        f"vite.config.server-entry.ts should reference tsconfig.server-entry.json\n"
        f"Content:\n{content}"
    )


def test_vue_start_vite_config_has_tsconfig_path():
    """
    Verify that vue-start's vite.config.server-entry.ts references tsconfig.server-entry.json.

    The vite config should have tsconfigPath: './tsconfig.server-entry.json' set.
    """
    vite_config_path = f"{VUE_START}/vite.config.server-entry.ts"

    assert os.path.exists(vite_config_path), (
        f"vite.config.server-entry.ts not found at {vite_config_path}"
    )

    with open(vite_config_path, 'r') as f:
        content = f.read()

    assert "tsconfigPath: './tsconfig.server-entry.json'" in content, (
        f"vite.config.server-entry.ts should reference tsconfig.server-entry.json\n"
        f"Content:\n{content}"
    )


def test_react_start_tsconfig_server_entry_exists():
    """
    Verify that react-start has a tsconfig.server-entry.json with correct rootDir.
    """
    tsconfig_path = f"{REACT_START}/tsconfig.server-entry.json"

    assert os.path.exists(tsconfig_path), (
        f"tsconfig.server-entry.json not found at {tsconfig_path}"
    )

    with open(tsconfig_path, 'r') as f:
        config = json.load(f)

    assert config.get("compilerOptions", {}).get("rootDir") == "./src/default-entry", (
        f"tsconfig.server-entry.json should have rootDir set to './src/default-entry'\n"
        f"Config: {config}"
    )

    assert "src/default-entry" in config.get("include", []), (
        f"tsconfig.server-entry.json should include 'src/default-entry'\n"
        f"Config: {config}"
    )


def test_solid_start_tsconfig_server_entry_exists():
    """
    Verify that solid-start has a tsconfig.server-entry.json with correct rootDir.
    """
    tsconfig_path = f"{SOLID_START}/tsconfig.server-entry.json"

    assert os.path.exists(tsconfig_path), (
        f"tsconfig.server-entry.json not found at {tsconfig_path}"
    )

    with open(tsconfig_path, 'r') as f:
        config = json.load(f)

    assert config.get("compilerOptions", {}).get("rootDir") == "./src/default-entry", (
        f"tsconfig.server-entry.json should have rootDir set to './src/default-entry'\n"
        f"Config: {config}"
    )

    assert "src/default-entry" in config.get("include", []), (
        f"tsconfig.server-entry.json should include 'src/default-entry'\n"
        f"Config: {config}"
    )


def test_vue_start_tsconfig_server_entry_exists():
    """
    Verify that vue-start has a tsconfig.server-entry.json with correct rootDir.
    """
    tsconfig_path = f"{VUE_START}/tsconfig.server-entry.json"

    assert os.path.exists(tsconfig_path), (
        f"tsconfig.server-entry.json not found at {tsconfig_path}"
    )

    with open(tsconfig_path, 'r') as f:
        config = json.load(f)

    assert config.get("compilerOptions", {}).get("rootDir") == "./src/default-entry", (
        f"tsconfig.server-entry.json should have rootDir set to './src/default-entry'\n"
        f"Config: {config}"
    )

    assert "src/default-entry" in config.get("include", []), (
        f"tsconfig.server-entry.json should include 'src/default-entry'\n"
        f"Config: {config}"
    )
