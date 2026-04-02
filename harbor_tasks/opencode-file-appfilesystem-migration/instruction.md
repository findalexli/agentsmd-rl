# File service bypasses AppFileSystem abstraction

## Summary

The `File` service in `packages/opencode/src/file/index.ts` directly uses raw `Filesystem` calls (like `Filesystem.exists`, `Filesystem.readText`, `Filesystem.readBytes`) wrapped inside `Effect.promise` blocks, instead of going through the `AppFileSystem` abstraction layer defined in `packages/opencode/src/filesystem/index.ts`.

This is inconsistent with the project's Effect conventions — effectified services should prefer yielding existing Effect services over dropping down to ad-hoc platform APIs. The `AppFileSystem` service already wraps the underlying `FileSystem` with traced helpers, but the `File` service never yields it and instead reaches through to the raw filesystem.

## Problems

1. **`read` method**: The entire method is wrapped in `Effect.promise(async () => { ... })` and uses `Filesystem.exists()`, `Filesystem.readText()`, `Filesystem.readBytes()` directly — none of which are traced through `AppFileSystem`.

2. **`list` method**: Similarly wrapped in `Effect.promise`, uses `Filesystem.exists()`, `Filesystem.readText()` for gitignore reading, and raw `fs.promises.readdir(resolved, { withFileTypes: true })` for listing directory entries.

3. **Missing capabilities on AppFileSystem**: The `AppFileSystem.Interface` may need to be extended with additional helpers to fully support the `File` service's needs (e.g., the `File` service does existence checks and directory listing in ways that `AppFileSystem` doesn't currently wrap).

4. **Layer composition**: The `File` namespace doesn't properly compose with `AppFileSystem`'s layer, making it harder to provide all required dependencies.

## Expected Behavior

- The `File` layer should yield `AppFileSystem.Service` and use its methods for all filesystem operations.
- `AppFileSystem` should be extended with the missing capabilities needed by the `File` service.
- The `File` namespace should export a `defaultLayer` that provides `AppFileSystem.defaultLayer`.
- The `read` and `list` methods should use Effect-native operations instead of `Effect.promise` wrappers around raw async calls (except where truly needed, e.g., git subprocess calls).

## Files to Investigate

- `packages/opencode/src/file/index.ts` — the `read` and `list` methods, and the layer definition
- `packages/opencode/src/filesystem/index.ts` — the `AppFileSystem` interface and implementation
