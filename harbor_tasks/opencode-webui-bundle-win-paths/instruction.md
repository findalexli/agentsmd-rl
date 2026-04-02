# Web UI bundle build fails on Windows

## Summary

The `createEmbeddedWebUIBundle` function in `packages/opencode/script/build.ts` generates JavaScript import statements for all files in the web UI dist directory. On Windows, this produces broken import paths because:

1. `Bun.Glob.scan()` returns paths with backslash separators (`assets\style.css`) on Windows, and these are used directly as export keys without normalization.
2. The import specifiers are constructed using `path.join()` which produces absolute paths with backslashes on Windows (e.g., `C:\Users\...\app\dist\index.html`). JavaScript import specifiers must use forward slashes and should be relative paths.
3. The generated file list order is non-deterministic across runs.

## Relevant Code

Look at the `createEmbeddedWebUIBundle` async function in `packages/opencode/script/build.ts` (around line 68). It scans the `../../app/dist` directory and generates a TypeScript module string with import statements and a default export mapping filenames to imported file handles.

## Expected Behavior

- All file paths in the generated module (both import specifiers and export keys) should use forward slashes regardless of platform.
- Import specifiers should be relative paths (starting with `./` or `../`), not absolute paths.
- The file list should be sorted for deterministic output across builds.

## Hints

- The `dir` variable (defined earlier in the file as the package root) is available and useful for computing relative paths.
- Consider `path.relative()` for generating relative import specifiers.
- `JSON.stringify()` is safer than manual quoting for import specifier strings.
