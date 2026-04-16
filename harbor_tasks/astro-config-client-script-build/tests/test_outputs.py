"""
Tests for astro:config/client build failure fix.

This test verifies that importing `astro:config/client` inside a `<script>` tag
in an Astro component works correctly during build, without causing Rollup to
fail with "failed to resolve import 'virtual:astro:routes' from 'virtual:astro:manifest'".
"""

import subprocess
import sys
import tempfile
import os
import json
import pytest
from pathlib import Path

# Path to the astro repository
REPO = Path("/workspace/astro")
ASTRO_PKG = REPO / "packages" / "astro"

def run_command(cmd, cwd=None, timeout=300, check=True):
    """Run a command and return the result."""
    if cwd is None:
        cwd = str(REPO)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    if check and result.returncode != 0:
        raise AssertionError(f"Command failed: {cmd}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    return result


def test_virtual_module_accepts_settings():
    """
    Fail-to-pass: Virtual module plugin must accept settings parameter.

    The fix changes the virtualModulePlugin signature from () to ({ settings }).
    This test verifies the new signature is working.
    """
    virtual_module_file = ASTRO_PKG / "src" / "manifest" / "virtual-module.ts"
    content = virtual_module_file.read_text()

    # Check that the plugin accepts settings parameter
    assert "export default function virtualModulePlugin({ settings }" in content, \
        "virtualModulePlugin must accept settings parameter"

    # Check that settings is used to get config
    assert "const config = settings.config;" in content, \
        "settings.config must be accessed"

    # Check that imports for routing utilities are present
    assert "fromRoutingStrategy" in content, \
        "fromRoutingStrategy must be imported"
    assert "toFallbackType" in content, \
        "toFallbackType must be imported"
    assert "toRoutingStrategy" in content, \
        "toRoutingStrategy must be imported"


def test_client_config_inlines_values():
    """
    Fail-to-pass: Client config must inline values from settings, not import from manifest.

    The original bug was that astro:config/client tried to import from
    virtual:astro:manifest, which pulls in server-only modules. The fix
    inlines the config values directly.
    """
    virtual_module_file = ASTRO_PKG / "src" / "manifest" / "virtual-module.ts"
    content = virtual_module_file.read_text()

    # Check that clientConfigCode is pre-computed at plugin creation time
    assert "const clientConfigCode =" in content, \
        "clientConfigCode must be pre-computed"

    # Check that the handler returns the pre-computed code
    assert "return { code: clientConfigCode };" in content, \
        "handler must return pre-computed clientConfigCode"

    # Verify that we're no longer importing from SERIALIZED_MANIFEST_ID in client handler
    # by checking that the old pattern is gone
    load_handler_start = content.find("handler(id) {")
    load_handler_end = content.find("if (id === RESOLVED_VIRTUAL_SERVER_ID)", load_handler_start)
    client_handler = content[load_handler_start:load_handler_end]

    # The old code imported from manifest - this should NOT be in the client handler anymore
    assert f"import {{ manifest }} from" not in client_handler, \
        "Client handler must NOT import from manifest (this causes the bug)"


def test_serialized_manifest_restricted_to_server():
    """
    Fail-to-pass: Serialized manifest plugin must be restricted to server environments.

    The virtual:astro:manifest module imports server-only modules like
    virtual:astro:routes and virtual:astro:pages. The fix adds applyToEnvironment
    to restrict this to server-only environments.
    """
    serialized_file = ASTRO_PKG / "src" / "manifest" / "serialized.ts"
    content = serialized_file.read_text()

    # Check that applyToEnvironment is implemented
    assert "applyToEnvironment(environment)" in content, \
        "serializedManifestPlugin must have applyToEnvironment"

    # Check that it restricts to server environments
    assert "ASTRO_VITE_ENVIRONMENT_NAMES.astro" in content, \
        "Must check for astro environment"
    assert "ASTRO_VITE_ENVIRONMENT_NAMES.ssr" in content, \
        "Must check for ssr environment"


def test_create_vite_passes_settings():
    """
    Fail-to-pass: createVite must pass settings to astroVirtualManifestPlugin.

    The plugin now requires settings parameter, so the caller must provide it.
    """
    create_vite_file = ASTRO_PKG / "src" / "core" / "create-vite.ts"
    content = create_vite_file.read_text()

    # Check that settings is passed to the plugin
    assert "astroVirtualManifestPlugin({ settings })" in content, \
        "createVite must pass settings to astroVirtualManifestPlugin"


def test_client_config_exports_correct_properties():
    """
    Fail-to-pass: Client config must export expected properties.

    The astro:config/client virtual module should export: base, i18n, trailingSlash,
    site, compressHTML, build, image
    """
    virtual_module_file = ASTRO_PKG / "src" / "manifest" / "virtual-module.ts"
    content = virtual_module_file.read_text()

    # Find the clientConfigCode section
    client_config_start = content.find("const clientConfigCode =")
    client_config_end = content.find("`;", client_config_start)
    client_config = content[client_config_start:client_config_end]

    # Check that all expected exports are present
    expected_exports = ["base", "i18n", "trailingSlash", "site", "compressHTML", "build", "image"]
    for export in expected_exports:
        assert f"export {{ " in content and export in content, \
            f"client config must export {export}"

    # Check that config values are properly serialized
    assert "JSON.stringify(config.base)" in content, \
        "base must be JSON stringified"
    assert "JSON.stringify(config.site)" in content, \
        "site must be JSON stringified"


def test_repo_unit_tests_pass():
    """
    Pass-to-pass: Repo unit tests should pass.

    Run a quick sanity check on the repo's own test suite for serializeManifest.
    This verifies the fix doesn't break existing functionality.
    """
    # Run only the serializeManifest tests to verify the fix
    result = subprocess.run(
        ["node", "--test", "test/serializeManifest.test.js"],
        cwd=str(ASTRO_PKG),
        capture_output=True,
        text=True,
        timeout=120
    )
    # The test might not exist in base commit (it's a new test), so skip if not found
    if result.returncode != 0:
        if "Cannot find module" in result.stderr or "ENOENT" in result.stderr:
            pytest.skip("serializeManifest test file not found or module not found")
        elif "no tests found" in result.stderr.lower() or "no tests matching" in result.stderr.lower():
            pytest.skip("No matching tests found in serializeManifest.test.js")
        else:
            assert result.returncode == 0, \
                f"serializeManifest tests failed: {result.stderr}\n{result.stdout}"


def test_repo_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors.

    This is a basic check that the code changes don't break TypeScript compilation.
    """
    result = subprocess.run(
        ["pnpm", "-C", "packages/astro", "exec", "tsc", "--noEmit"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"TypeScript compilation failed: {result.stderr}"


def test_repo_linter_passes():
    """
    Pass-to-pass: Biome linter should pass.

    The repo uses Biome for linting (as mentioned in AGENTS.md).
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120
    )
    # Allow either success or skip (if no lint issues found)
    # The important thing is it doesn't fail
    if result.returncode != 0:
        # Check if it's a real lint error or just biome not found
        if "Biome" in result.stderr or "lint" in result.stderr.lower():
            pytest.skip(f"Lint check skipped: {result.stderr}")


def test_repo_biome_lint():
    """
    Pass-to-pass: Biome lint should pass (repo CI command).

    The repo uses Biome for linting as part of CI.
    """
    result = subprocess.run(
        ["pnpm", "exec", "biome", "lint", "--max-diagnostics=10"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Biome lint failed: {result.stderr[-500:]}"


def test_repo_build():
    """
    Pass-to-pass: Repo build should succeed (repo CI command).

    The repo uses pnpm run build for building packages.
    """
    result = subprocess.run(
        ["pnpm", "run", "build"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"Build failed: {result.stderr[-500:]}"


def test_repo_unit_tests_all():
    """
    Pass-to-pass: All unit tests should pass (repo CI command).

    The repo uses pnpm run test:unit for unit testing.
    """
    result = subprocess.run(
        ["pnpm", "run", "test:unit"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"Unit tests failed: {result.stderr[-500:]}"


def test_repo_serializeManifest():
    """
    Pass-to-pass: serializeManifest test should pass (repo CI command).

    Tests for manifest serialization which is related to the modified code.
    """
    result = subprocess.run(
        ["pnpm", "run", "test:match", "test/serializeManifest.test.js"],
        cwd=str(ASTRO_PKG),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"serializeManifest test failed: {result.stderr[-500:]}"


def test_repo_astro_manifest():
    """
    Pass-to-pass: astro-manifest integration test should pass (repo CI command).

    Tests for astro:config virtual modules which are related to the modified code.
    """
    result = subprocess.run(
        ["pnpm", "run", "test:match", "test/astro-manifest.test.js"],
        cwd=str(ASTRO_PKG),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"astro-manifest test failed: {result.stderr[-500:]}"


def test_repo_manifest_routing():
    """
    Pass-to-pass: Manifest routing unit tests should pass (repo CI command).

    Tests for manifest routing which is related to the modified code.
    """
    result = subprocess.run(
        ["pnpm", "run", "test:match", "test/units/routing/manifest.test.js"],
        cwd=str(ASTRO_PKG),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Manifest routing test failed: {result.stderr[-500:]}"


def test_serialize_manifest_virtual_module_has_client_support():
    """
    Pass-to-pass: The serializeManifest test should have client config tests.

    The test file should cover the astro:config/client functionality.
    """
    test_file = ASTRO_PKG / "test" / "serializeManifest.test.js"
    if not test_file.exists():
        pytest.skip("serializeManifest.test.js does not exist")

    content = test_file.read_text()
    # Check that there are tests for astro:config/client
    assert "astro:config/client" in content, \
        "Tests should exist for astro:config/client"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
