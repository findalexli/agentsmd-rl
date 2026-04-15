# Add sourcemaps and a debug build to Angular DevTools

## Problem

Angular DevTools currently has no debug build mode. All builds are minified, making it difficult to inspect and debug the extension during development. There's no way to build and load an unminified version of the extension with sourcemaps.

The esbuild configuration for DevTools scripts has two issues:
1. Scripts injected into web pages (`detect-angular.ts`, `backend.ts`, `ng-validate.ts`, `content-script.ts`) need inline sourcemaps because Chrome requires inline sourcemaps for injected scripts - linked sourcemaps don't work in that context
2. The `minify = True` setting is hardcoded in multiple BUILD files, preventing any centralized control over minification

## Requirements

The following behavioral changes must be implemented:

1. **Debug flag in `devtools/BUILD.bazel`**:
   - The build must expose a boolean flag named `debug` that can be set via `--//devtools:debug` on the bazel command line
   - A config setting named `debug_build` must match when the debug flag is set to `"True"`

2. **Configurable esbuild in `devtools/tools/defaults.bzl`**:
   - The esbuild function must accept `minify` and `sourcemap` parameters
   - Minification must be disabled when the debug configuration is active, enabled by default (when no explicit minify value is provided)
   - The esbuild wrapper must delegate to an internal esbuild implementation

3. **Inline sourcemaps for injected scripts in `devtools/projects/shell-browser/src/app/BUILD.bazel`**:
   - The esbuild targets for `detect-angular.ts`, `backend.ts`, `ng-validate.ts`, and `content-script.ts` must have `sourcemap = "inline"`
   - These targets must not hardcode `minify = True`

4. **Remove hardcoded minification in `devtools/projects/shell-browser/src/BUILD.bazel`**:
   - All esbuild calls must have their hardcoded `minify = True` removed so the centralized debug flag can control minification

5. **Debug build npm scripts in `package.json`**:
   - A script named `devtools:build:chrome:debug` must pass `--//devtools:debug` to bazel and reference `devtools:build:chrome`
   - A script named `devtools:build:firefox:debug` must pass `--//devtools:debug` to bazel and reference `devtools:build:firefox`

## Files to Look At

- `devtools/tools/defaults.bzl` — shared Bazel build defaults, currently re-exports esbuild directly
- `devtools/BUILD.bazel` — top-level devtools Bazel config
- `devtools/projects/shell-browser/src/BUILD.bazel` — main shell browser build targets
- `devtools/projects/shell-browser/src/app/BUILD.bazel` — individual script build targets (backend, content script, etc.)
- `package.json` — npm scripts for building devtools
