# Add sourcemaps and a debug build to Angular DevTools

## Problem

Angular DevTools currently has no debug build mode. All builds are minified, making it difficult to inspect and debug the extension during development. There's no way to build and load an unminified version of the extension with sourcemaps, and the devtools README doesn't explain how to install or debug a local build of the extension.

## What needs to change

1. **Add a debug build flag**: Create a Bazel build flag that controls whether builds are minified. In debug mode, minification should be disabled. The flag should be usable from the command line.

2. **Enable sourcemaps**: Add sourcemaps to all DevTools builds. For scripts that are injected into the page (like content scripts, backend, and detection scripts), Chrome requires inline sourcemaps — linked sourcemaps don't work for these.

3. **Add debug build npm scripts**: Add convenient `pnpm` scripts for building the extension in debug mode for both Chrome and Firefox.

4. **Remove hardcoded minification**: The shell-browser source BUILD files currently hardcode `minify = True` on individual esbuild targets. This should be removed so the centralized debug flag can control it.

5. **Update the devtools README**: After making the build changes, update `devtools/README.md` to document:
   - How to build and install a dev version of the extension
   - Where to find and debug the various extension scripts (panel UI, content scripts, background worker, etc.)

## Files to Look At

- `devtools/tools/defaults.bzl` — shared Bazel build defaults, currently re-exports esbuild directly
- `devtools/BUILD.bazel` — top-level devtools Bazel config
- `devtools/projects/shell-browser/src/BUILD.bazel` — main shell browser build targets
- `devtools/projects/shell-browser/src/app/BUILD.bazel` — individual script build targets (backend, content script, etc.)
- `package.json` — npm scripts for building devtools
- `devtools/README.md` — developer documentation for the devtools extension
