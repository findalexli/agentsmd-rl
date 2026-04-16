"""Tests for file descriptor leak fixes in Astro integrations."""

import subprocess
import os
import tempfile
import time
import sys

REPO = "/workspace/astro"
NODE_INTEGRATION = f"{REPO}/packages/integrations/node"
PARTYTOWN_INTEGRATION = f"{REPO}/packages/integrations/partytown"


def test_partytown_stream_cleanup():
    """
    Verify that sirv.ts has the stream.destroy() cleanup for client disconnects.

    This is a fail-to-pass test: the base code leaks file descriptors because
    createReadStream().pipe(res) doesn't cleanup when the response closes early.
    """
    sirv_path = f"{PARTYTOWN_INTEGRATION}/src/sirv.ts"
    with open(sirv_path, 'r') as f:
        content = f.read()

    # Check that stream is captured and destroyed on response close
    assert "const stream = fs.createReadStream(file, opts)" in content, \
        "Stream should be captured in a variable"
    assert "stream.pipe(res)" in content, \
        "Stream should be piped to response"
    assert "res.on('close', () => stream.destroy())" in content, \
        "Stream must be destroyed when response closes to prevent fd leak"


def test_node_serve_app_stream_cleanup():
    """
    Verify that serve-app.ts destroys streams on error to prevent fd leaks.

    This is a fail-to-pass test: the base code leaves streams open when
    errors occur in the retry loop, leaking file descriptors across iterations.
    """
    serve_app_path = f"{NODE_INTEGRATION}/src/serve-app.ts"
    with open(serve_app_path, 'r') as f:
        content = f.read()

    # Check stream is declared outside try block
    assert "let stream: ReturnType<typeof createReadStream> | undefined" in content, \
        "Stream must be declared outside try block for catch accessibility"

    # Check stream is assigned inside try
    assert "stream = createReadStream(fullPath)" in content, \
        "Stream should be assigned to the outer variable"

    # Check stream is destroyed in catch block
    assert "stream?.destroy()" in content, \
        "Stream must be destroyed in catch block to release fd on error"


def test_typescript_compiles():
    """
    Verify TypeScript compiles without errors (pass-to-pass).

    The fix must not break type checking.
    """
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=NODE_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_biome_lint():
    """
    Verify Biome linting passes (pass-to-pass).

    The repo uses Biome for linting/formatting.
    """
    result = subprocess.run(
        ["pnpm", "exec", "biome", "check", "src/serve-app.ts"],
        cwd=NODE_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout}\n{result.stderr}"


def test_partytown_typescript_compiles():
    """
    Verify partytown TypeScript compiles without errors (pass-to-pass).
    """
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=PARTYTOWN_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_node_build_ci():
    """
    Verify node integration builds successfully (pass-to-pass).

    The repo's CI uses 'pnpm run build:ci' to compile the package.
    """
    result = subprocess.run(
        ["pnpm", "run", "build:ci"],
        cwd=NODE_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_partytown_build_ci():
    """
    Verify partytown integration builds successfully (pass-to-pass).

    The repo's CI uses 'pnpm run build:ci' to compile the package.
    """
    result = subprocess.run(
        ["pnpm", "run", "build:ci"],
        cwd=PARTYTOWN_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_node_unit_tests():
    """
    Verify node integration unit tests pass (pass-to-pass).

    Runs the isolated unit tests in test/units/ that don't require network.
    """
    result = subprocess.run(
        ["node", "--test", "test/units/*.test.js"],
        cwd=NODE_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_partytown_biome_lint():
    """
    Verify Biome linting passes for partytown sirv.ts (pass-to-pass).

    The repo uses Biome for linting/formatting.
    """
    result = subprocess.run(
        ["pnpm", "exec", "biome", "check", "src/sirv.ts"],
        cwd=PARTYTOWN_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout}\n{result.stderr}"


def test_node_unit_tests_serve_static():
    """
    Verify node integration serve-static-path unit tests pass (pass-to-pass).

    Tests resolveStaticPath which is used alongside the stream cleanup code
    in serve-app.ts. This validates the file serving logic is sound.
    """
    result = subprocess.run(
        ["node", "--test", "test/units/serve-static-path-traversal.test.js"],
        cwd=NODE_INTEGRATION,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"serve-static unit tests failed:\n{result.stderr[-500:]}"


def test_biome_lint_modified_files():
    """
    Verify Biome linting passes on both modified source files (pass-to-pass).

    Runs the repo's Biome linter on the files modified by the fix.
    """
    result = subprocess.run(
        ["pnpm", "exec", "biome", "lint", "packages/integrations/node/src/serve-app.ts",
         "packages/integrations/partytown/src/sirv.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
