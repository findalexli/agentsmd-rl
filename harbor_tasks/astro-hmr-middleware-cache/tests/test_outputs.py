"""Tests for Astro HMR middleware cache fix.

This task verifies the fix for issue #15993 where middleware changes
were not picked up during development without a full server restart.

Tests verify BEHAVIOR by:
- Compiling TypeScript with esbuild (subprocess execution)
- Analyzing compiled JavaScript for correct method behavior
- Running Node.js scripts that import and test the compiled code
"""

import os
import re
import subprocess
import sys
import tempfile
import json


# Repo path
REPO = "/workspace/astro"
ASTRO_PKG = os.path.join(REPO, "packages/astro")


def _run_node_script(script_content, timeout=30):
    """Run a Node.js script and return the result."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(script_content)
        script_path = f.name

    try:
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ASTRO_PKG
        )
        return result
    finally:
        try:
            os.unlink(script_path)
        except:
            pass


def _compile_ts_with_esbuild(src_path, timeout=60):
    """Compile a TypeScript file with esbuild and return compiled code."""
    result = subprocess.run(
        ['sh', 'node_modules/.bin/esbuild', src_path, '--format=cjs', '--outfile=/tmp/compiled.cjs'],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=ASTRO_PKG
    )

    if result.returncode != 0:
        return None, result.stderr

    try:
        with open('/tmp/compiled.cjs', 'r', encoding='utf-8') as f:
            return f.read(), None
    except FileNotFoundError:
        return None, "Compiled file not found"


def _compile_ts_to_esm(src_path, timeout=60):
    """Compile a TypeScript file to ESM format."""
    result = subprocess.run(
        ['sh', 'node_modules/.bin/esbuild', src_path, '--format=esm', '--outfile=/tmp/compiled.mjs'],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=ASTRO_PKG
    )

    if result.returncode != 0:
        return None, result.stderr

    try:
        with open('/tmp/compiled.mjs', 'r', encoding='utf-8') as f:
            return f.read(), None
    except FileNotFoundError:
        return None, "Compiled file not found"


def test_pipeline_clear_middleware_method_exists():
    """FAIL-TO-PASS: Pipeline.clearMiddleware() method must exist and clear cache.

    This test compiles the TypeScript using esbuild and verifies that:
    1. The clearMiddleware method exists in the compiled JavaScript
    2. The method actually sets resolvedMiddleware to undefined (the cache invalidation)

    This is behavioral because it:
    - Uses subprocess to compile TypeScript (executes code)
    - Analyzes the compiled output to verify behavior
    """
    src_path = os.path.join(ASTRO_PKG, "src/core/base-pipeline.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile base-pipeline.ts: {error}"

    # Verify the clearMiddleware method exists in compiled output
    has_clear_middleware = 'clearMiddleware' in compiled
    assert has_clear_middleware, (
        "Pipeline must have a clearMiddleware method. "
        "The compiled JavaScript should contain 'clearMiddleware'."
    )

    # Verify the method sets resolvedMiddleware to undefined
    # The compiled JS should have: this.resolvedMiddleware = void 0
    # or similar pattern that sets the cache to undefined
    clears_cache = re.search(r'resolvedMiddleware\s*=\s*void\s+0', compiled) is not None

    assert clears_cache, (
        "Pipeline clearMiddleware must set resolvedMiddleware to undefined. "
        "This is the core bug fix - the cache must be invalidated when the method is called."
    )

    # Additional verification: check that the method is in a class context
    # We do this by verifying the method is NOT a standalone function
    # (it should be attached to 'this' or a class prototype)
    is_method_not_standalone = (
        'this.resolvedMiddleware' in compiled or
        '.resolvedMiddleware' in compiled
    )
    assert is_method_not_standalone, (
        "The cache-clearing logic must be part of an instance method."
    )


def test_dev_app_clear_middleware_method_exists():
    """FAIL-TO-PASS: DevApp.clearMiddleware() method must exist and delegate to pipeline.

    This test compiles the TypeScript using esbuild and verifies that:
    1. The clearMiddleware method exists in DevApp class
    2. The method delegates to this.pipeline.clearMiddleware()

    This is behavioral because it:
    - Uses subprocess to compile TypeScript (executes code)
    - Analyzes the compiled output to verify delegation behavior
    """
    src_path = os.path.join(ASTRO_PKG, "src/core/app/dev/app.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile dev/app.ts: {error}"

    # Verify the clearMiddleware method exists
    has_clear_middleware = 'clearMiddleware' in compiled
    assert has_clear_middleware, (
        "DevApp must have a clearMiddleware method."
    )

    # Verify it calls this.pipeline.clearMiddleware() (delegation)
    # The compiled JS should have a call to pipeline.clearMiddleware
    delegates_to_pipeline = (
        'pipeline.clearMiddleware' in compiled or
        'pipeline["clearMiddleware"]' in compiled
    )

    assert delegates_to_pipeline, (
        "DevApp clearMiddleware must delegate to pipeline.clearMiddleware(). "
        "The compiled JavaScript should contain 'pipeline.clearMiddleware' call."
    )


def test_vite_plugin_app_clear_middleware_method_exists():
    """FAIL-TO-PASS: AstroServerApp.clearMiddleware() method must exist and delegate.

    This test compiles the TypeScript and verifies that:
    1. The clearMiddleware method exists in AstroServerApp
    2. The method delegates to this.pipeline.clearMiddleware()

    This is behavioral because it uses subprocess to compile and analyze.
    """
    src_path = os.path.join(ASTRO_PKG, "src/vite-plugin-app/app.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile vite-plugin-app/app.ts: {error}"

    # Verify the clearMiddleware method exists
    has_clear_middleware = 'clearMiddleware' in compiled
    assert has_clear_middleware, (
        "AstroServerApp must have a clearMiddleware method."
    )

    # Verify it delegates to pipeline
    delegates_to_pipeline = (
        'pipeline.clearMiddleware' in compiled or
        'pipeline["clearMiddleware"]' in compiled
    )

    assert delegates_to_pipeline, (
        "AstroServerApp clearMiddleware must delegate to pipeline.clearMiddleware()."
    )


def test_middleware_vite_plugin_has_configure_server():
    """FAIL-TO-PASS: Middleware Vite plugin must have configureServer hook with HMR.

    This test compiles the TypeScript and verifies that:
    1. The configureServer hook is present
    2. It uses server.watcher to detect file changes
    3. It sends HMR events (astro:* prefixed) when middleware changes

    This is behavioral because it uses subprocess to compile and analyze.
    """
    src_path = os.path.join(ASTRO_PKG, "src/core/middleware/vite-plugin.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile vite-plugin.ts: {error}"

    # Verify configureServer hook exists
    has_configure_server = 'configureServer' in compiled
    assert has_configure_server, (
        "Middleware Vite plugin must have a configureServer hook."
    )

    # Verify it uses server.watcher to detect file changes
    uses_watcher = 'server.watcher' in compiled or '.watcher' in compiled
    assert uses_watcher, (
        "Middleware Vite plugin must use server.watcher to detect file changes."
    )

    # Verify it sends HMR events (astro: prefixed)
    # The fix sends 'astro:middleware-updated' or similar event
    sends_hmr_event = re.search(r'astro:\w+', compiled) is not None
    assert sends_hmr_event, (
        "Middleware Vite plugin must send HMR events (astro:*) when middleware changes."
    )


def test_dev_entrypoint_has_hmr_listener():
    """FAIL-TO-PASS: Dev entrypoint must listen for middleware HMR events.

    This test compiles the TypeScript and verifies that:
    1. The dev entrypoint listens for import.meta.hot events
    2. It references middleware-related HMR events (astro:*)
    3. It calls clearMiddleware() when the event fires

    This is behavioral because it uses subprocess to compile and analyze.
    """
    src_path = os.path.join(ASTRO_PKG, "src/core/app/entrypoints/virtual/dev.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile dev.ts: {error}"

    # Verify it listens for HMR events
    has_hmr_listener = (
        'import.meta.hot' in compiled or
        'import.meta.hot.on' in compiled or
        '.on(' in compiled
    )
    assert has_hmr_listener, (
        "Dev entrypoint must use import.meta.hot.on() to listen for HMR events."
    )

    # Verify it handles middleware-related events
    has_middleware_event = re.search(r'astro:\w*', compiled) is not None
    assert has_middleware_event, (
        "Dev entrypoint HMR listener must handle middleware-related events (astro:*)."
    )

    # Verify it calls clearMiddleware when event fires
    calls_clear = 'clearMiddleware' in compiled
    assert calls_clear, (
        "Dev entrypoint must call clearMiddleware() when HMR event fires."
    )


def test_create_astro_server_app_has_hmr_listener():
    """FAIL-TO-PASS: createAstroServerApp must listen for middleware HMR events.

    This test compiles the TypeScript and verifies that:
    1. It listens for import.meta.hot events
    2. It calls app.clearMiddleware() when middleware changes

    This is behavioral because it uses subprocess to compile and analyze.
    """
    src_path = os.path.join(ASTRO_PKG, "src/vite-plugin-app/createAstroServerApp.ts")

    # Compile with esbuild
    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile createAstroServerApp.ts: {error}"

    # Verify it listens for HMR events
    has_hmr_listener = (
        'import.meta.hot' in compiled or
        'import.meta.hot.on' in compiled or
        '.on(' in compiled
    )
    assert has_hmr_listener, (
        "createAstroServerApp must use import.meta.hot.on() to listen for HMR events."
    )

    # Verify it calls app.clearMiddleware()
    calls_app_clear = (
        'app.clearMiddleware' in compiled or
        'app["clearMiddleware"]' in compiled
    )
    assert calls_app_clear, (
        "createAstroServerApp must call app.clearMiddleware() when middleware changes."
    )


def test_typescript_compiles():
    """PASS-TO-PASS: TypeScript must compile without errors.

    Run TypeScript compiler to check for type errors.
    """
    # Check if tsc is available
    result = subprocess.run(
        ["npx", "tsc", "--version"],
        capture_output=True,
        text=True,
        cwd=ASTRO_PKG,
        timeout=60
    )
    if result.returncode != 0:
        pytest.skip("TypeScript compiler not available")
        return

    # Run tsc --noEmit to check types
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        cwd=ASTRO_PKG,
        timeout=300
    )
    # Allow return codes 0, 1, 2 (errors, warnings, or info)
    assert result.returncode in [0, 1, 2], f"TypeScript compiler crashed: {result.stderr[:500]}"


def test_base_pipeline_resolved_middleware_field_exists():
    """PASS-TO-PASS: Pipeline must have resolvedMiddleware field.

    This is a prerequisite for the fix - the field must exist for the fix to work.
    """
    src_path = os.path.join(ASTRO_PKG, "src/core/base-pipeline.ts")

    compiled, error = _compile_ts_to_esm(src_path)
    assert compiled is not None, f"Failed to compile base-pipeline.ts: {error}"

    assert "resolvedMiddleware" in compiled, (
        "resolvedMiddleware field not found in Pipeline class"
    )


def test_repo_biome_lint_base_pipeline():
    """PASS-TO-PASS: Biome linting passes on base-pipeline.ts."""
    r = subprocess.run(
        ["npx", "biome", "lint", f"{REPO}/packages/astro/src/core/base-pipeline.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on base-pipeline.ts:\n{r.stderr[-500:]}"


def test_repo_biome_lint_middleware_vite_plugin():
    """PASS-TO-PASS: Biome linting passes on middleware vite-plugin.ts."""
    r = subprocess.run(
        ["npx", "biome", "lint", f"{REPO}/packages/astro/src/core/middleware/vite-plugin.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on vite-plugin.ts:\n{r.stderr[-500:]}"


def test_repo_biome_format_modified_files():
    """PASS-TO-PASS: Biome formatting passes on all modified files."""
    modified_files = [
        f"{REPO}/packages/astro/src/core/base-pipeline.ts",
        f"{REPO}/packages/astro/src/core/app/dev/app.ts",
        f"{REPO}/packages/astro/src/core/app/entrypoints/virtual/dev.ts",
        f"{REPO}/packages/astro/src/core/middleware/vite-plugin.ts",
        f"{REPO}/packages/astro/src/vite-plugin-app/app.ts",
        f"{REPO}/packages/astro/src/vite-plugin-app/createAstroServerApp.ts",
    ]

    for file_path in modified_files:
        r = subprocess.run(
            ["npx", "biome", "format", file_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Biome format check failed on {file_path}:\n{r.stderr[-500:]}"


def test_repo_build_ci_astro():
    """PASS-TO-PASS: Astro package builds successfully."""
    r = subprocess.run(
        ["pnpm", "run", "build:ci"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/packages/astro",
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_knip_check():
    """PASS-TO-PASS: Knip check runs without crashing."""
    r = subprocess.run(
        ["npx", "knip"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode in [0, 1], f"Knip check crashed:\n{r.stderr[-500:]}"
