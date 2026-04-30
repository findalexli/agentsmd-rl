# Resolve extensionless relative imports in the TS-to-ESM loader

## Context

`code/core/src/bin/loader.ts` is a Node `LoadHook`. When Storybook is launched
with `--import` pointing at this loader, Node delegates `.ts` / `.tsx` /
`.mts` / `.cts` files to it, and the hook converts them to ESM via esbuild
before handing the source back to Node.

Node's ESM resolver requires **explicit file extensions** on relative
imports. Many users wrote configuration like:

```ts
// .storybook/main.ts
import { foo } from './test-import';   // no extension
```

After esbuild transforms this file, the import specifier is unchanged.
Node then tries to resolve `./test-import` as a literal path, fails, and the
whole Storybook process crashes with `ERR_MODULE_NOT_FOUND`.

For TypeScript-based preset/config files we want to be lenient: detect the
extensionless relative import, probe the filesystem for a sibling file with
a known JS/TS extension, and rewrite the specifier in-place — while warning
the user that the extensionless form is deprecated.

## What you must change

Edit only `code/core/src/bin/loader.ts`. Add **two new exported
functions** and wire one of them into the existing `load` hook so the
transformed source emitted to Node has its extensions added.

### 1. `resolveWithExtension(importPath: string, currentFilePath: string): string`

Resolve a single import specifier to a path that includes a file extension.

- If `importPath` already has a file extension (anything that
  `path.extname` reports as non-empty), **return it unchanged** and do
  **not** emit any warning. This is the fast path.
- Otherwise, emit a deprecation warning by calling `deprecate(...)` from
  `storybook/internal/node-logger`. The warning message **must contain
  every one of these literal substrings** (each is asserted independently
  by the tests):
  - `One or more extensionless imports detected: "<importPath>"` — with
    the actual import path interpolated inside the double quotes.
  - `in file "<currentFilePath>"` — with the actual current file path
    interpolated inside the double quotes.
  - `For maximum compatibility, you should add an explicit file extension`
- After emitting the warning, attempt to resolve the import by appending
  each of the following extensions to the **absolute** path
  (`path.resolve(path.dirname(currentFilePath), importPath)`) and checking
  `existsSync` on the candidate:
  `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts`, `.tsx`.
  Return the **original** `importPath` with the matching extension
  appended (e.g. `./utils` → `./utils.ts`) — **not** the absolute path.
- If no candidate exists, return the original `importPath` unchanged
  (the warning has already been emitted).

### 2. `addExtensionsToRelativeImports(source: string, filePath: string): string`

Given a chunk of transpiled JavaScript (`source`) and the originating file
path, return a new source string in which every relative import/export
specifier has been replaced by `resolveWithExtension(specifier, filePath)`.

The function must handle all of the following syntactic forms (these are
the only forms exercised by the tests):

- **Static imports**: `import x from './a';`,
  `import { x, y } from './a';`, `import * as ns from './a';`,
  side-effect form `import './a';`, default+named, and the multi-line
  variants (newlines between `{` and `}`).
- **Static exports**: `export { x } from './a';`, `export * from './a';`,
  multi-line forms.
- **Dynamic imports** with single, double, or backtick-quoted strings:
  `import('./a')`, `import("./a")`, `` import(`./a`) ``, including
  multi-line whitespace inside the parentheses.

It must **not** touch:

- Bare specifiers (`react`, `@scope/pkg`, `node:fs`).
- Specifiers that already have a file extension.
- Specifiers that don't begin with `./` or `../` (e.g. `.config`).
- Backtick dynamic imports that contain a `${…}` template interpolation
  (e.g. `` import(`./${foo}/bar`) `` and `` import(`${foo}/bar`) ``) —
  the path is a runtime value and cannot be statically rewritten.

Both single-quoted and double-quoted strings must be supported in the
output, preserving whichever quote style the input used.

### 3. Wire it into the `load` hook

The existing `load: LoadHook` already runs `esbuild.transform(...)` on
`.ts` / `.tsx` / `.mts` / `.cts` (and the rare `.mtsx` / `.ctsx`)
sources. After the transform completes, run the transformed code through
`addExtensionsToRelativeImports` (using the file path obtained via
`fileURLToPath(url)`) and return that rewritten source from the hook
instead of the raw `transformedSource.code`.

## Imports you may need

The file currently imports `readFile` from `node:fs/promises`,
`fileURLToPath` from `node:url`, `transform` from `esbuild`, and a
`NODE_TARGET` constant. For your additions you will also need
`existsSync` from `node:fs`, `path` from `node:path`, `deprecate` from
`storybook/internal/node-logger`, and `dedent` from `ts-dedent` (used to
clean up multi-line warning text).

## Constraints

- Only `code/core/src/bin/loader.ts` may be edited.
- Both new functions must be **named exports** so the test file can do
  `import { addExtensionsToRelativeImports, resolveWithExtension } from './loader';`.
- The existing `load` export must continue to be the default behaviour for
  non-TS URLs (it already calls `nextLoad(url, context)` for them — keep
  that).
- Do not introduce new runtime dependencies beyond `ts-dedent`,
  `storybook/internal/node-logger`, and the Node built-ins listed above
  (these are already declared in `package.json`).

## Code Style Requirements

- TypeScript **strict mode** is enabled (`tsc --strict --noEmit` is part
  of the test suite); make sure your additions type-check cleanly.
- Follow the existing import-grouping and naming style of `loader.ts`.

## How your work will be tested

A vitest suite imports `addExtensionsToRelativeImports` and
`resolveWithExtension` from `./loader`, mocks `node:fs` and
`storybook/internal/node-logger`, and exercises every form listed above.
A separate end-to-end driver imports the **real** (unmocked) loader and
runs both functions against a small fixture. Your code must pass both.
