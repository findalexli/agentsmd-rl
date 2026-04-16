"""
Fail-to-pass (f2p) and pass-to-pass (p2p) tests for the middleware HMR fix.

The PR withastro/astro#16054 fixes middleware changes not being picked up during
`astro dev` without a full server restart.

Tests verify the structural and behavioral changes needed for this fix.
Behavioral tests compile TypeScript with esbuild and inspect the resulting JS.
"""

import os
import re
import subprocess
import sys
import tempfile
import json

# The repo is checked out at /workspace/astro
REPO = "/workspace/astro"


def esbuild_compile(src_path):
    """Compile a TypeScript file with esbuild and return the JS output."""
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        r = subprocess.run(
            ["npx", "esbuild", src_path, "--outfile=" + tmp_path,
             "--format=esm", "--platform=node", "--target=node18"],
            capture_output=True, text=True, cwd=REPO, timeout=60
        )
        if r.returncode != 0:
            return None, r.stderr
        with open(tmp_path) as f:
            return f.read(), None
    finally:
        os.unlink(tmp_path)


def get_method_body(js_content, class_name, method_name):
    """Extract the body of a method from compiled JS class."""
    pattern = rf'{method_name}\s*\([^)]*\)\s*\{{([^}}]*(?:\{{[^}}]*\}}[^}}]*)*)\}}'
    m = re.search(pattern, js_content, re.DOTALL)
    return m.group(1) if m else None


def method_exists(js_content, method_name):
    """Check if a method exists in the compiled JS."""
    pattern = rf'{re.escape(method_name)}\s*\('
    return bool(re.search(pattern, js_content))


def call_expression_exists(js_content, call_target):
    """Check if a specific function/method call exists in JS."""
    return bool(re.search(rf'\b{re.escape(call_target)}\s*\(', js_content))


def event_listener_exists(js_content, event_name):
    """Check if an event listener for the given event exists."""
    escaped_event = re.escape(event_name)
    pattern = rf"import\.meta\.hot\.on\s*\(\s*['\"]{escaped_event}"
    return bool(re.search(pattern, js_content))


def hot_send_exists(js_content, event_name):
    """Check if hot.send() for the given event exists."""
    escaped_event = re.escape(event_name)
    pattern = rf"hot\.send\s*\(\s*['\"]{escaped_event}"
    return bool(re.search(pattern, js_content))


def watcher_on_change_exists(js_content):
    """Check if server.watcher.on(\"change\", ...) exists."""
    return bool(re.search(r'server\.watcher\.on\s*\(\s*["\']change["\']', js_content))


class TestPipelineClearMiddleware:
    """Tests for Pipeline.clearMiddleware() method (compiled + behavioral)."""

    def test_pipeline_has_clear_middleware_method(self):
        """Pipeline class must have clearMiddleware method that can be called (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/base-pipeline.ts")
        js_out, err = esbuild_compile(path)
        assert err is None or "error" not in err.lower(), f"esbuild failed: {err}"
        assert js_out is not None, "esbuild produced no output"
        assert method_exists(js_out, "clearMiddleware"), \
            "Pipeline must have clearMiddleware method for HMR to work"

    def test_clear_middleware_unsets_resolved_middleware(self):
        """clearMiddleware() must reset resolvedMiddleware to undefined/void 0 (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/base-pipeline.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"

        assert method_exists(js_out, "clearMiddleware"), \
            "clearMiddleware method must exist"

        body = get_method_body(js_out, "Pipeline", "clearMiddleware")
        assert body is not None, "clearMiddleware method body not found"
        # TypeScript undefined compiles to void 0 in JS, also check for literal "undefined"
        assert re.search(r'resolvedMiddleware\s*=\s*(undefined|void 0)', body), \
            "clearMiddleware() must reset resolvedMiddleware to undefined"


class TestAstroServerAppClearMiddleware:
    """Tests for AstroServerApp.clearMiddleware() method (compiled + behavioral)."""

    def test_astroserverapp_has_clear_middleware(self):
        """AstroServerApp must have clearMiddleware method that calls pipeline.clearMiddleware (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/vite-plugin-app/app.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"
        assert method_exists(js_out, "clearMiddleware"), \
            "AstroServerApp must have clearMiddleware method for HMR to work"

        body = get_method_body(js_out, "AstroServerApp", "clearMiddleware")
        assert body is not None, "AstroServerApp.clearMiddleware body not found"
        assert call_expression_exists(body, "pipeline.clearMiddleware"), \
            "AstroServerApp.clearMiddleware must call pipeline.clearMiddleware()"


class TestDevAppClearMiddleware:
    """Tests for DevApp.clearMiddleware() method (compiled + behavioral)."""

    def test_devapp_has_clear_middleware(self):
        """DevApp must have clearMiddleware method that calls pipeline.clearMiddleware (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/app/dev/app.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"
        assert method_exists(js_out, "clearMiddleware"), \
            "DevApp must have clearMiddleware method for HMR to work"

        body = get_method_body(js_out, "DevApp", "clearMiddleware")
        assert body is not None, "DevApp.clearMiddleware body not found"
        assert call_expression_exists(body, "pipeline.clearMiddleware"), \
            "DevApp.clearMiddleware must call pipeline.clearMiddleware()"


class TestMiddlewarePluginConfigureServer:
    """Tests for the middleware vite plugin's configureServer hook (compiled + behavioral)."""

    def test_vite_plugin_has_configure_server(self):
        """vitePluginMiddleware must have configureServer hook (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/middleware/vite-plugin.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"
        assert method_exists(js_out, "configureServer"), \
            "vitePluginMiddleware must have configureServer hook to watch middleware files"

    def test_configure_server_watches_middleware_files(self):
        """configureServer must watch for changes and send HMR event (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/middleware/vite-plugin.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"

        assert watcher_on_change_exists(js_out), \
            "configureServer must register a watcher 'change' handler"

        assert hot_send_exists(js_out, "astro:middleware-updated"), \
            "configureServer must send 'astro:middleware-updated' HMR event"

        assert re.search(r'srcDir', js_out), \
            "configureServer must check if changed file is under srcDir"


class TestVirtualDevHMR:
    """Tests for HMR event listener in virtual dev module (compiled + behavioral)."""

    def test_virtual_dev_listens_for_middleware_updated(self):
        """createApp in virtual/dev.ts must listen for astro:middleware-updated and call clearMiddleware (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/core/app/entrypoints/virtual/dev.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"

        assert event_listener_exists(js_out, "astro:middleware-updated"), \
            "virtual/dev.ts must listen for 'astro:middleware-updated' HMR event"

        assert call_expression_exists(js_out, "clearMiddleware"), \
            "virtual/dev.ts must call clearMiddleware when HMR event fires"


class TestCreateAstroServerAppHMR:
    """Tests for HMR event listener in createAstroServerApp (compiled + behavioral)."""

    def test_create_astro_server_app_listens_for_middleware_updated(self):
        """createAstroServerApp must listen for astro:middleware-updated and call clearMiddleware (f2p)."""
        path = os.path.join(REPO, "packages/astro/src/vite-plugin-app/createAstroServerApp.ts")
        js_out, err = esbuild_compile(path)
        assert js_out is not None, f"esbuild failed: {err}"

        assert event_listener_exists(js_out, "astro:middleware-updated"), \
            "createAstroServerApp.ts must listen for 'astro:middleware-updated' HMR event"

        assert call_expression_exists(js_out, "clearMiddleware"), \
            "createAstroServerApp.ts must call clearMiddleware when HMR event fires"


class TestIntegrationHMRBehavior:
    """Integration test: verify the end-to-end HMR behavior chain exists."""

    def test_hmr_chain_exists_in_code(self):
        """Verify the complete HMR chain: watcher -> event -> clearMiddleware (f2p)."""
        vite_plugin = os.path.join(REPO, "packages/astro/src/core/middleware/vite-plugin.ts")
        virtual_dev = os.path.join(REPO, "packages/astro/src/core/app/entrypoints/virtual/dev.ts")
        create_app = os.path.join(REPO, "packages/astro/src/vite-plugin-app/createAstroServerApp.ts")
        pipeline = os.path.join(REPO, "packages/astro/src/core/base-pipeline.ts")

        vite_js, _ = esbuild_compile(vite_plugin)
        virtual_js, _ = esbuild_compile(virtual_dev)
        create_js, _ = esbuild_compile(create_app)
        pipeline_js, _ = esbuild_compile(pipeline)

        assert all([vite_js, virtual_js, create_js, pipeline_js]), \
            "All modules must compile successfully"

        assert hot_send_exists(vite_js, "astro:middleware-updated"), \
            "Vite plugin must send astro:middleware-updated event"

        assert event_listener_exists(virtual_js, "astro:middleware-updated"), \
            "virtual/dev must listen for the HMR event"
        assert call_expression_exists(virtual_js, "clearMiddleware"), \
            "virtual/dev must call clearMiddleware"

        assert event_listener_exists(create_js, "astro:middleware-updated"), \
            "createAstroServerApp must listen for the HMR event"
        assert call_expression_exists(create_js, "clearMiddleware"), \
            "createAstroServerApp must call clearMiddleware"

        assert method_exists(pipeline_js, "clearMiddleware"), \
            "Pipeline must have clearMiddleware"
        body = get_method_body(pipeline_js, "Pipeline", "clearMiddleware")
        assert body and re.search(r'resolvedMiddleware\s*=\s*(undefined|void 0)', body), \
            "Pipeline.clearMiddleware must reset resolvedMiddleware"


class TestRepoLint:
    """Pass-to-pass test: repo's linter should pass on fixed code."""

    def test_biome_lint_passes(self):
        """Repo's Biome linter passes on all modified files (p2p)."""
        r = subprocess.run(
            ["npx", "biome", "check",
             "packages/astro/src/core/base-pipeline.ts",
             "packages/astro/src/vite-plugin-app/app.ts",
             "packages/astro/src/core/app/dev/app.ts",
             "packages/astro/src/core/middleware/vite-plugin.ts",
             "packages/astro/src/vite-plugin-app/createAstroServerApp.ts",
             "packages/astro/src/core/app/entrypoints/virtual/dev.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Biome lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

    def test_eslint_passes(self):
        """Repo's ESLint passes on modified directories (p2p)."""
        r = subprocess.run(
            ["pnpm", "run", "eslint:ci"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

    def test_biome_check_all_modified_files(self):
        """Repo's Biome check passes on all modified files (p2p)."""
        r = subprocess.run(
            ["npx", "biome", "check",
             "packages/astro/src/core/base-pipeline.ts",
             "packages/astro/src/vite-plugin-app/app.ts",
             "packages/astro/src/core/app/dev/app.ts",
             "packages/astro/src/core/middleware/vite-plugin.ts",
             "packages/astro/src/vite-plugin-app/createAstroServerApp.ts",
             "packages/astro/src/core/app/entrypoints/virtual/dev.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Biome check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
