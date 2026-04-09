# Turbopack: Move turbopack out of `pnpm build` and into `pnpm build-all`

## Problem

The `pnpm build` command currently always triggers the `maybe-build-native` script in `packages/next-swc`, which compiles the Rust/Turbopack code. This causes issues for developers who have already compiled a custom version of Turbopack with specific flags or profiles, because there's no way to build only the JavaScript parts without also recompiling Turbopack.

Additionally, the turbo.json configuration uses the name `build` for the native build task, which is confusing alongside the standard `build` script.

## Expected Behavior

1. `pnpm build` should only build JavaScript code (via `turbo run build`)
2. A new `pnpm build-all` command should build both JavaScript and Rust/Turbopack code
3. The native build task in `packages/next-swc` should be renamed from `build` to `build-native-auto` to clarify its purpose
4. The turbo.json file should be renamed to turbo.jsonc (JSON with comments) and updated with the new task names
5. `AGENTS.md` should be updated to document the new build commands

## Files to Modify

- `package.json` — Add `build-all` script
- `packages/next-swc/package.json` — Rename `build` script to `build-native-auto`
- `packages/next-swc/turbo.json` → `packages/next-swc/turbo.jsonc` — Rename and update task names
- `AGENTS.md` — Update build command documentation

## Key Changes

**Root package.json:** Add this script:
```json
"build-all": "turbo run build build-native-auto --remote-cache-timeout 60 --summarize true"
```

**packages/next-swc/package.json:** Change:
```json
"build": "node maybe-build-native.mjs"
```
to:
```json
"build-native-auto": "node maybe-build-native.mjs"
```

**packages/next-swc/turbo.jsonc:** Rename the file and update the task from `"build"` to `"build-native-auto"` with a comment explaining the purpose.

**AGENTS.md:** Update references from `pnpm build` to `pnpm build-all` where full builds (including Turbopack) are needed.
