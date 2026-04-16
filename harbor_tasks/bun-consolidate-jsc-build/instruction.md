# Consolidate jsc:build into build.ts, add BUN_WEBKIT_PATH support

## Problem

The Bun project's build system has several issues that need addressing:

1. **Standalone build-jsc.ts script exists**: There is a `scripts/build-jsc.ts` file that exists outside the consolidated build system. This should be removed and its functionality properly integrated.

2. **package.json scripts reference obsolete file**: The `jsc:build`, `jsc:build:debug`, and `jsc:build:lto` npm scripts currently call `scripts/build-jsc.ts` directly instead of routing through the main build system entry point at `scripts/build.ts`.

3. **Clean presets reference wrong directories**: The `scripts/build/clean.ts` file contains references to `vendor/WebKit/WebKitBuild` in preset descriptions. These references are incorrect for local builds which now use `build/<profile>/deps/WebKit/` paths.

4. **No support for shared WebKit clone**: Developers working across multiple Bun worktrees need a way to share a single WebKit clone. The system currently does not support a `BUN_WEBKIT_PATH` environment variable for specifying an alternative WebKit source path, nor does it implement path resolution with home directory expansion (tilde `~` support).

5. **Local source type lacks path override and error hints**: The local source type in `scripts/build/source.ts` needs to support:
   - An optional path property for absolute path overrides when resolving local dependencies
   - An optional hint property for custom error messages when a source is not found

6. **Documentation table needs reformatting**: The "Module inventory" table in `scripts/build/CLAUDE.md` needs to be reformatted to use wider column alignment consistent with other sections.

## Acceptance Criteria

- `scripts/build-jsc.ts` must not exist
- All `jsc:build*` npm scripts must reference `build.ts` with `--target=WebKit`
- `scripts/build/clean.ts` must not contain "WebKitBuild" or "vendor/WebKit"
- `scripts/build/deps/webkit.ts` must support an alternative WebKit source path via environment variable, with path resolution that handles tilde expansion, and must provide helpful error messages when a local source is not found
- `scripts/build/source.ts` must define optional path and hint properties for local sources, and use these properties during resolution and error handling
- `scripts/build/CLAUDE.md` must have a reformatted table with wider columns containing entries for `build.ts`, `clean.ts`, `source.ts`, and `deps/*.ts`
- All modified TypeScript files must have valid syntax