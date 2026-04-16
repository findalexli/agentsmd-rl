"""
Tests for TanStack Router PR #7035: Fix missing declaration files for server-entry exports.

The bug: With TypeScript 6's change from inferred rootDir to defaulting to `.`,
vite-plugin-dts emits declarations at the wrong nested path. Without the fix,
declaration files end up at `dist/default-entry/esm/src/default-entry/server.d.ts`
instead of the correct `dist/default-entry/esm/server.d.ts` path.

The fix: Add tsconfig.server-entry.json files with explicit rootDir configuration
and reference them in vite.config.server-entry.ts via tsconfigPath.
"""

import subprocess
import os
from pathlib import Path

REPO = Path("/workspace/router")
PACKAGES = ["react-start", "solid-start", "vue-start"]


def test_react_start_server_entry_dts_path():
    """
    Build react-start and verify server.d.ts is at the correct path (fail_to_pass).

    Without the fix, declaration files are nested under src/default-entry/.
    With the fix, they should be directly under dist/default-entry/esm/.
    """
    pkg_dir = REPO / "packages" / "react-start"

    # Clean dist directory first
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        subprocess.run(["rm", "-rf", str(dist_dir)], check=True)

    # Build the package
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-start:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"

    # Check that the declaration file exists at the CORRECT path
    correct_path = pkg_dir / "dist" / "default-entry" / "esm" / "server.d.ts"
    assert correct_path.exists(), (
        f"Declaration file missing at correct path: {correct_path}\n"
        f"This indicates the rootDir fix was not applied."
    )

    # Check that the declaration file does NOT exist at the WRONG nested path
    wrong_path = pkg_dir / "dist" / "default-entry" / "esm" / "src" / "default-entry" / "server.d.ts"
    assert not wrong_path.exists(), (
        f"Declaration file found at wrong nested path: {wrong_path}\n"
        f"This indicates rootDir is not correctly set in tsconfig.server-entry.json."
    )


def test_solid_start_server_entry_dts_path():
    """
    Build solid-start and verify server.d.ts is at the correct path (fail_to_pass).
    """
    pkg_dir = REPO / "packages" / "solid-start"

    # Clean dist directory first
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        subprocess.run(["rm", "-rf", str(dist_dir)], check=True)

    # Build the package
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-start:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"

    # Check that the declaration file exists at the CORRECT path
    correct_path = pkg_dir / "dist" / "default-entry" / "esm" / "server.d.ts"
    assert correct_path.exists(), (
        f"Declaration file missing at correct path: {correct_path}\n"
        f"This indicates the rootDir fix was not applied."
    )

    # Check that the declaration file does NOT exist at the WRONG nested path
    wrong_path = pkg_dir / "dist" / "default-entry" / "esm" / "src" / "default-entry" / "server.d.ts"
    assert not wrong_path.exists(), (
        f"Declaration file found at wrong nested path: {wrong_path}\n"
        f"This indicates rootDir is not correctly set in tsconfig.server-entry.json."
    )


def test_vue_start_server_entry_dts_path():
    """
    Build vue-start and verify server.d.ts is at the correct path (fail_to_pass).
    """
    pkg_dir = REPO / "packages" / "vue-start"

    # Clean dist directory first
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        subprocess.run(["rm", "-rf", str(dist_dir)], check=True)

    # Build the package
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-start:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"

    # Check that the declaration file exists at the CORRECT path
    correct_path = pkg_dir / "dist" / "default-entry" / "esm" / "server.d.ts"
    assert correct_path.exists(), (
        f"Declaration file missing at correct path: {correct_path}\n"
        f"This indicates the rootDir fix was not applied."
    )

    # Check that the declaration file does NOT exist at the WRONG nested path
    wrong_path = pkg_dir / "dist" / "default-entry" / "esm" / "src" / "default-entry" / "server.d.ts"
    assert not wrong_path.exists(), (
        f"Declaration file found at wrong nested path: {wrong_path}\n"
        f"This indicates rootDir is not correctly set in tsconfig.server-entry.json."
    )


def test_tsconfig_server_entry_exists_react():
    """
    Verify tsconfig.server-entry.json exists with correct rootDir for react-start (fail_to_pass).
    """
    tsconfig_path = REPO / "packages" / "react-start" / "tsconfig.server-entry.json"
    assert tsconfig_path.exists(), f"Missing {tsconfig_path}"

    content = tsconfig_path.read_text()
    assert '"rootDir": "./src/default-entry"' in content, (
        f"tsconfig.server-entry.json missing rootDir configuration:\n{content}"
    )


def test_tsconfig_server_entry_exists_solid():
    """
    Verify tsconfig.server-entry.json exists with correct rootDir for solid-start (fail_to_pass).
    """
    tsconfig_path = REPO / "packages" / "solid-start" / "tsconfig.server-entry.json"
    assert tsconfig_path.exists(), f"Missing {tsconfig_path}"

    content = tsconfig_path.read_text()
    assert '"rootDir": "./src/default-entry"' in content, (
        f"tsconfig.server-entry.json missing rootDir configuration:\n{content}"
    )


def test_tsconfig_server_entry_exists_vue():
    """
    Verify tsconfig.server-entry.json exists with correct rootDir for vue-start (fail_to_pass).
    """
    tsconfig_path = REPO / "packages" / "vue-start" / "tsconfig.server-entry.json"
    assert tsconfig_path.exists(), f"Missing {tsconfig_path}"

    content = tsconfig_path.read_text()
    assert '"rootDir": "./src/default-entry"' in content, (
        f"tsconfig.server-entry.json missing rootDir configuration:\n{content}"
    )


def test_vite_config_references_tsconfig_react():
    """
    Verify vite.config.server-entry.ts references the new tsconfig for react-start (fail_to_pass).
    """
    vite_config = REPO / "packages" / "react-start" / "vite.config.server-entry.ts"
    content = vite_config.read_text()
    assert "tsconfigPath:" in content and "tsconfig.server-entry.json" in content, (
        f"vite.config.server-entry.ts must reference tsconfig.server-entry.json:\n{content}"
    )


def test_vite_config_references_tsconfig_solid():
    """
    Verify vite.config.server-entry.ts references the new tsconfig for solid-start (fail_to_pass).
    """
    vite_config = REPO / "packages" / "solid-start" / "vite.config.server-entry.ts"
    content = vite_config.read_text()
    assert "tsconfigPath:" in content and "tsconfig.server-entry.json" in content, (
        f"vite.config.server-entry.ts must reference tsconfig.server-entry.json:\n{content}"
    )


def test_vite_config_references_tsconfig_vue():
    """
    Verify vite.config.server-entry.ts references the new tsconfig for vue-start (fail_to_pass).
    """
    vite_config = REPO / "packages" / "vue-start" / "vite.config.server-entry.ts"
    content = vite_config.read_text()
    assert "tsconfigPath:" in content and "tsconfig.server-entry.json" in content, (
        f"vite.config.server-entry.ts must reference tsconfig.server-entry.json:\n{content}"
    )


def test_repo_router_core_types():
    """
    Run TypeScript type checking for router-core (pass_to_pass).

    This validates that the core types compile correctly across multiple TS versions.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stderr[-2000:]}"


def test_repo_history_unit_tests():
    """
    Run unit tests for the history package (pass_to_pass).

    This validates the history package which is a dependency of the router packages.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/history:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"


def test_repo_router_core_unit_tests():
    """
    Run unit tests for the router-core package (pass_to_pass).

    This validates the router-core package which is the foundation for all router packages.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"


def test_repo_router_core_build_validation():
    """
    Run build validation (publint + attw) for router-core (pass_to_pass).

    This validates the package exports and type correctness using CI tooling.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build validation failed:\n{result.stderr[-2000:]}"


def test_repo_history_build_validation():
    """
    Run build validation (publint + attw) for history package (pass_to_pass).

    This validates the history package exports and type correctness.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/history:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build validation failed:\n{result.stderr[-2000:]}"
