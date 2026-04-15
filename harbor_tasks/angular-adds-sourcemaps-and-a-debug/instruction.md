# Add sourcemaps and a debug build to Angular DevTools

## Problem

Angular DevTools currently has no debug build mode. All builds are minified, making it difficult to inspect and debug the extension during development. There's no way to build and load an unminified version of the extension with sourcemaps, and the devtools README doesn't explain how to install or debug a local build of the extension.

## What needs to change

1. **Add a debug build flag**: Create a Bazel `bool_flag` named `debug` and a `config_setting` named `debug_build` in `devtools/BUILD.bazel`. The config setting should match when `:debug` is set to `"True"`. This flag will control whether builds are minified. In debug mode, minification should be disabled.

2. **Create an esbuild wrapper**: In `devtools/tools/defaults.bzl`, create a wrapper function named `esbuild` (defined with `def esbuild(...)`) that accepts `minify` and `sourcemap` parameters. The wrapper should use `select()` to conditionally set minify based on the `//devtools:debug_build` configuration: `//devtools:debug_build` should set minify to `False`, and `//conditions:default` should set minify to `True`. The wrapper must internally call a function named `_esbuild(` with the resolved parameters.

3. **Enable inline sourcemaps for injected scripts**: For the following scripts that are injected into the page, set `sourcemap = "inline"` in their esbuild targets (Chrome requires inline sourcemaps for injected scripts - linked sourcemaps don't work):
   - `detect-angular.ts`
   - `backend.ts`
   - `ng-validate.ts`
   - `content-script.ts`

4. **Remove hardcoded minification**: The shell-browser source BUILD files (`devtools/projects/shell-browser/src/BUILD.bazel` and `devtools/projects/shell-browser/src/app/BUILD.bazel`) currently have `minify = True` hardcoded on individual esbuild targets. Remove all `minify = True` settings so the centralized debug flag can control it.

5. **Add debug build npm scripts**: Add two pnpm scripts to `package.json`:
   - `devtools:build:chrome:debug` — must pass `--//devtools:debug` flag when invoking bazel
   - `devtools:build:firefox:debug` — must pass `--//devtools:debug` flag when invoking bazel
   Both scripts should chain from their respective base scripts (`devtools:build:chrome` and `devtools:build:firefox`).

6. **Update the devtools README**: Update `devtools/README.md` to document:
   - How to build and install a dev version of the extension
   - Where to find and debug the various extension scripts (panel UI, content scripts, background worker, etc.)

## Files to Look At

- `devtools/tools/defaults.bzl` — shared Bazel build defaults, currently re-exports esbuild directly
- `devtools/BUILD.bazel` — top-level devtools Bazel config
- `devtools/projects/shell-browser/src/BUILD.bazel` — main shell browser build targets
- `devtools/projects/shell-browser/src/app/BUILD.bazel` — individual script build targets (backend, content script, etc.)
- `package.json` — npm scripts for building devtools
- `devtools/README.md` — developer documentation for the devtools extension
