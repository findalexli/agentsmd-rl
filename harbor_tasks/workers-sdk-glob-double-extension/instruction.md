# Glob Pattern Matching Bug in Miniflare

## Symptom

Module rules with glob patterns like `**/*.wasm` are incorrectly matching files that have `.wasm` as a substring within their name, such as:
- `foo.wasm.js`
- `main.wasm.test.ts`
- `file.wasm.map`

When using `@cloudflare/vitest-pool-workers` with a `wrangler.configPath`, test files whose names contain `.wasm` are being silently loaded as WebAssembly modules instead of JavaScript/TypeScript, causing runtime failures.

## Expected Behavior

A glob pattern `**/*.wasm` should:
- Match: `foo.wasm`, `path/to/foo.wasm`, `/absolute/path/to/foo.wasm`
- NOT match: `foo.wasm.js`, `main.wasm.test.ts`, `file.wasm.map`

The `globsToRegExps` function accepts an options object. When the `endAnchor` option is set to `true`, patterns should only match paths that end with the glob pattern, preventing double-extension matches.

The `testRegExps` function can be used to verify whether a given path matches the compiled patterns.

The `compileModuleRules` function should produce matchers that correctly distinguish between `.wasm` files and files like `.wasm.js`.

## Build and Test Commands

After the fix is applied, these commands should all succeed:
```
pnpm run build --filter miniflare
pnpm run check:type -F miniflare
pnpm test -F miniflare matcher
```

## Relevant Files

The miniflare package lives at `packages/miniflare/` in the workspace. The existing matcher tests at `packages/miniflare/test/shared/matcher.spec.ts` should continue to pass.