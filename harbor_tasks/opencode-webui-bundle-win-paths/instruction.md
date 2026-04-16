# Web UI bundle build fails on Windows

## Summary

The opencode project has a build script at `packages/opencode/script/build.ts` containing a function named `createEmbeddedWebUIBundle` that generates a TypeScript module string by scanning the web UI dist directory. The generated module contains import statements and a default export mapping file paths to imported modules.

On Windows, the build output is broken because:

1. File paths from the glob scan may contain backslash separators (`\`), and these are used directly as export keys without normalization to forward slashes (`/`).
2. Import specifiers are constructed as absolute OS paths. JavaScript import specifiers must use forward slashes and should be relative paths (starting with `./` or `../`).
3. The generated file list order is non-deterministic across runs.

## Expected Behavior

The `createEmbeddedWebUIBundle` function must produce output that satisfies all of the following:

- **Forward slashes**: All file paths in the generated module (both import specifiers and export keys) must use forward slashes (`/`) regardless of platform.
- **Relative import specifiers**: Import specifiers must be relative paths starting with `./` or `../`, not absolute paths.
- **Sorted output**: The file list must be sorted alphabetically for deterministic output across builds.
- **All files present**: All scanned dist files must appear in the generated module output.
- **Valid module structure**: The output must have `import` statements, `export default`, and a `type: "file"` annotation.

## Coding Style Requirements

The project has an `AGENTS.md` file at the repo root with coding style conventions. Your fix must comply with the rules listed in AGENTS.md for lines 70, 17, 13, 12, 84, and 15 (rules cover: const-only declarations, no imperative loops, no `any` type, no try/catch, no `else` statements, and using Bun.Glob for file scanning).