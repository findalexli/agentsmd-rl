#!/usr/bin/env python3
"""Apply the HMR middleware fix to Astro codebase."""

import os
import re
import sys

BASE_DIR = "/workspace/astro/packages/astro"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def check_already_applied():
    """Check if the patch was already applied."""
    content = read_file(os.path.join(BASE_DIR, "src/core/base-pipeline.ts"))
    return "clearMiddleware()" in content

def fix_base_pipeline():
    """Add clearMiddleware() to Pipeline class."""
    path = os.path.join(BASE_DIR, "src/core/base-pipeline.ts")
    content = read_file(path)

    if "clearMiddleware()" in content:
        print("  base-pipeline.ts: already patched")
        return

    # Find the line with "async getActions():" and insert before it
    lines = content.split("\n")
    insert_idx = None

    for i, line in enumerate(lines):
        if "async getActions():" in line:
            insert_idx = i
            break

    if insert_idx is None:
        print("  ERROR: Could not find insertion point in base-pipeline.ts")
        sys.exit(1)

    new_method = [
        "\t/**",
        "\t * Clears the cached middleware so it is re-resolved on the next request.",
        "\t * Called via HMR when middleware files change during development.",
        "\t */",
        "\tclearMiddleware(): void {",
        "\t\tthis.resolvedMiddleware = undefined;",
        "\t}",
        "",
    ]

    lines = lines[:insert_idx] + new_method + lines[insert_idx:]
    write_file(path, "\n".join(lines))
    print("  base-pipeline.ts: patched")

def fix_dev_app():
    """Add clearMiddleware() to DevApp class."""
    path = os.path.join(BASE_DIR, "src/core/app/dev/app.ts")
    content = read_file(path)

    if "clearMiddleware(): void" in content:
        print("  dev/app.ts: already patched")
        return

    # Find updateRoutes method and add clearMiddleware after it
    lines = content.split("\n")
    insert_idx = None

    for i, line in enumerate(lines):
        if "updateRoutes(newRoutesList: RoutesList): void {" in line:
            # Find the closing brace of this method
            brace_count = 1
            j = i + 1
            while j < len(lines) and brace_count > 0:
                if "{" in lines[j]:
                    brace_count += lines[j].count("{")
                if "}" in lines[j]:
                    brace_count -= lines[j].count("}")
                j += 1
            insert_idx = j
            break

    if insert_idx is None:
        print("  ERROR: Could not find insertion point in dev/app.ts")
        sys.exit(1)

    new_method = [
        "",
        "\t/**",
        "\t * Clears the cached middleware so it is re-resolved on the next request.",
        "\t * Called via HMR when middleware files change.",
        "\t */",
        "\tclearMiddleware(): void {",
        "\t\tthis.pipeline.clearMiddleware();",
        "\t}",
    ]

    lines = lines[:insert_idx] + new_method + lines[insert_idx:]
    write_file(path, "\n".join(lines))
    print("  dev/app.ts: patched")

def fix_dev_entrypoint():
    """Add HMR listener to dev.ts entrypoint."""
    path = os.path.join(BASE_DIR, "src/core/app/entrypoints/virtual/dev.ts")
    content = read_file(path)

    if "astro:middleware-updated" in content:
        print("  dev.ts: already patched")
        return

    # Find the astro:content-changed handler and add after it
    lines = content.split("\n")
    insert_idx = None

    for i, line in enumerate(lines):
        if "astro:content-changed" in line:
            # Find the closing brace of this handler (the });)
            brace_count = 1
            j = i + 1
            while j < len(lines) and brace_count > 0:
                if "{" in lines[j]:
                    brace_count += lines[j].count("{")
                if "}" in lines[j]:
                    brace_count -= lines[j].count("}")
                j += 1
            insert_idx = j
            break

    if insert_idx is None:
        print("  ERROR: Could not find insertion point in dev.ts")
        sys.exit(1)

    new_handler = [
        "",
        "\t\t// Listen for middleware file changes via HMR.",
        "\t\t// Clear the cached middleware so it is re-resolved on the next request.",
        "\t\timport.meta.hot.on('astro:middleware-updated', () => {",
        "\t\t\tif (!currentDevApp) return;",
        "\t\t\tcurrentDevApp.clearMiddleware();",
        "\t\t});",
    ]

    lines = lines[:insert_idx] + new_handler + lines[insert_idx:]
    write_file(path, "\n".join(lines))
    print("  dev.ts: patched")

def fix_vite_plugin():
    """Add configureServer to middleware vite plugin."""
    path = os.path.join(BASE_DIR, "src/core/middleware/vite-plugin.ts")
    content = read_file(path)

    if "configureServer" in content:
        print("  vite-plugin.ts: already patched")
        return

    # Update imports
    content = content.replace(
        "import type { Plugin as VitePlugin } from 'vite';",
        """import { fileURLToPath } from 'node:url';
import {
\tnormalizePath as viteNormalizePath,
\ttype ViteDevServer,
\ttype Plugin as VitePlugin,
} from 'vite';"""
    )

    # Add normalizedSrcDir after userMiddlewareIsPresent declaration
    content = content.replace(
        "let userMiddlewareIsPresent = false;\n\n\treturn",
        """let userMiddlewareIsPresent = false;

\tconst normalizedSrcDir = viteNormalizePath(fileURLToPath(settings.config.srcDir));

\treturn"""
    )

    # Add configureServer after applyToEnvironment
    # Find the applyToEnvironment block and add after it
    pattern = r'(applyToEnvironment\(environment\)\s*\{[^}]+\},)'
    replacement = r'''\1
\t\tconfigureServer(server: ViteDevServer) {
\t\t\tserver.watcher.on('change', (path) => {
\t\t\t\tconst normalizedPath = viteNormalizePath(path);
\t\t\t\t// Check if the changed file is a middleware file under srcDir
\t\t\t\tif (!normalizedPath.startsWith(normalizedSrcDir)) return;
\t\t\t\tconst relativePath = normalizedPath.slice(normalizedSrcDir.length);
\t\t\t\t// Dot ensures we match "middleware.ts" but not e.g. "middleware-utils.ts"
\t\t\t\tif (!relativePath.startsWith(`${MIDDLEWARE_PATH_SEGMENT_NAME}.`)) return;

\t\t\t\tfor (const name of [
\t\t\t\t\tASTRO_VITE_ENVIRONMENT_NAMES.ssr,
\t\t\t\t\tASTRO_VITE_ENVIRONMENT_NAMES.astro,
\t\t\t\t] as const) {
\t\t\t\t\tconst environment = server.environments[name];
\t\t\t\t\tif (!environment) continue;

\t\t\t\t\tconst virtualMod = environment.moduleGraph.getModuleById(MIDDLEWARE_RESOLVED_MODULE_ID);
\t\t\t\t\tif (virtualMod) {
\t\t\t\t\t\tenvironment.moduleGraph.invalidateModule(virtualMod);
\t\t\t\t\t}

\t\t\t\t\tenvironment.hot.send('astro:middleware-updated', {});
\t\t\t\t}
\t\t\t});
\t\t},'''

    content = re.sub(pattern, replacement, content)

    write_file(path, content)
    print("  vite-plugin.ts: patched")

def fix_vite_plugin_app():
    """Add clearMiddleware() to AstroServerApp class."""
    path = os.path.join(BASE_DIR, "src/vite-plugin-app/app.ts")
    content = read_file(path)

    if "clearMiddleware(): void" in content:
        print("  vite-plugin-app/app.ts: already patched")
        return

    # Find clearRouteCache method and add clearMiddleware after it
    lines = content.split("\n")
    insert_idx = None

    for i, line in enumerate(lines):
        if "clearRouteCache(): void {" in line:
            # Find the closing brace of this method
            brace_count = 1
            j = i + 1
            while j < len(lines) and brace_count > 0:
                if "{" in lines[j]:
                    brace_count += lines[j].count("{")
                if "}" in lines[j]:
                    brace_count -= lines[j].count("}")
                j += 1
            insert_idx = j
            break

    if insert_idx is None:
        print("  ERROR: Could not find insertion point in vite-plugin-app/app.ts")
        sys.exit(1)

    new_method = [
        "",
        "\t/**",
        "\t * Clears the cached middleware so it is re-resolved on the next request.",
        "\t * Called via HMR when middleware files change.",
        "\t */",
        "\tclearMiddleware(): void {",
        "\t\tthis.pipeline.clearMiddleware();",
        "\t}",
    ]

    lines = lines[:insert_idx] + new_method + lines[insert_idx:]
    write_file(path, "\n".join(lines))
    print("  vite-plugin-app/app.ts: patched")

def fix_create_astro_server_app():
    """Add HMR listener to createAstroServerApp."""
    path = os.path.join(BASE_DIR, "src/vite-plugin-app/createAstroServerApp.ts")
    content = read_file(path)

    if "astro:middleware-updated" in content:
        print("  createAstroServerApp.ts: already patched")
        return

    # Find the route cache handler and add after it
    lines = content.split("\n")
    insert_idx = None

    for i, line in enumerate(lines):
        if "Route cache cleared due to content change" in line:
            # Find the }); that closes this handler
            brace_count = 1
            j = i + 1
            while j < len(lines) and brace_count > 0:
                if "{" in lines[j]:
                    brace_count += lines[j].count("{")
                if "}" in lines[j]:
                    brace_count -= lines[j].count("}")
                j += 1
            # Now we should be at }); - need to skip one more
            insert_idx = j
            break

    if insert_idx is None:
        print("  ERROR: Could not find insertion point in createAstroServerApp.ts")
        sys.exit(1)

    new_handler = [
        "",
        "\t\t// Listen for middleware file changes via HMR.",
        "\t\t// Clear the cached middleware so it is re-resolved on the next request.",
        "\t\timport.meta.hot.on('astro:middleware-updated', () => {",
        "\t\t\tapp.clearMiddleware();",
        "\t\t\tactualLogger.debug('router', 'Middleware cache cleared due to file change');",
        "\t\t});",
    ]

    lines = lines[:insert_idx] + new_handler + lines[insert_idx:]
    write_file(path, "\n".join(lines))
    print("  createAstroServerApp.ts: patched")

def main():
    print("Applying HMR middleware fix...")

    if check_already_applied():
        print("Patch already applied, skipping")
        sys.exit(0)

    fix_base_pipeline()
    fix_dev_app()
    fix_dev_entrypoint()
    fix_vite_plugin()
    fix_vite_plugin_app()
    fix_create_astro_server_app()

    print("\nAll patches applied successfully!")

if __name__ == "__main__":
    main()
