# Web UI bundle build fails on Windows

## Summary

The opencode project has a build script that generates a TypeScript module string by scanning the web UI dist directory. The generated module contains import statements and a default export mapping file paths to imported modules. On Windows, this produces broken output because:

1. File paths from the glob scan may contain backslash separators (`\`), and these are used directly as export keys without normalization to forward slashes (`/`).
2. Import specifiers are constructed as absolute OS paths. JavaScript import specifiers must use forward slashes and should be relative paths (starting with `./` or `../`).
3. The generated file list order is non-deterministic across runs.

## Expected Behavior

Fix the function that generates the embedded web UI bundle module string so the output satisfies all of the following:

- **Forward slashes**: All file paths in the generated module (both import specifiers and export keys) must use forward slashes (`/`) regardless of platform. The source code must contain explicit backslash-to-forward-slash normalization logic in the function body. Acceptable normalization approaches include: using `replaceAll` or `replace` with backslash target patterns, using `split("\\").join(...)`, using `path.posix` utilities, replacing `path.sep`, or defining a dedicated normalization helper function (e.g., named `toForwardSlash`, `normalizePath`, or `normalizeSlash`).
- **Relative import specifiers**: Import specifiers must be relative paths starting with `./` or `../`, not absolute paths.
- **Sorted output**: The file list must be sorted alphabetically for deterministic output across builds.
- **All files present**: All scanned dist files must appear in the generated module output.
- **Valid module structure**: The output must have `import` statements, `export default`, and a `type: "file"` annotation.

## Coding Style Requirements

The project has an `AGENTS.md` file at the repo root with coding style conventions. Your fix must comply with the following rules from `AGENTS.md`:

- **const only** (line 70): Use only `const` for variable declarations. Do not use `let` or `var`.
- **No imperative loops** (line 17): Do not use `for` or `while` loops. Use functional array methods like `map`, `filter`, `flatMap`, or `reduce` instead.
- **No `any` type** (line 13): Do not use the `any` type annotation (no `: any`, `as any`, or `<any>`).
- **No try/catch** (line 12): Do not use try/catch blocks.
- **No `else` statements** (line 84): Do not use `else`. Prefer early returns.
- **Use Bun.Glob** (line 15): Use `Bun.Glob` for file scanning. Prefer Bun APIs over the native `fs` module.
