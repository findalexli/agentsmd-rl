# Task: Refactor oxfmt CLI JS Config Handling

## Problem

The oxfmt formatter's CLI JavaScript configuration handling code needs reorganization. The current code has a disorganized file structure, tests are in a separate file from the code they test, and the error handling in `loadJsConfig()` does not consistently return an `Error` instance with context.

## Symptoms

1. **Loose files**: `cli/js_config.ts` and `cli/node_version.ts` are loose files without a parent directory
2. **Separate test file**: Tests for the node version hint logic are in `test/cli/js_config/node_version.test.ts` instead of co-located with the code
3. **Inconsistent error handling**: `loadJsConfig()` sometimes throws an `Error` and sometimes returns the hint as a separate string value — callers cannot rely on catching a single `Error` type with the hint appended to its message
4. **Test command issue**: The test command runs vitest with a `--dir` flag that is not needed for the desired test runner configuration

## Requirements

### Error Handling

The `loadJsConfig()` function must always throw an `Error` instance. Specifically:

- When loading a config file fails with a TypeScript module loading error, the implementation should call a function that generates a hint message for unsupported TypeScript module loading
- The hint (if any) should be appended to the original error's `message` property
- After appending the hint, the original error should be thrown
- The pattern should use `.catch()` with an error parameter, access `err.message`, and use `throw err`

The hint-generating function must be exported from the node version module and should be named `getUnsupportedTypeScriptModuleLoadHint`.

### File Organization

The JS config code should be organized under a `js_config/` directory:
- The main config loading logic should be in `js_config/index.ts`
- The node version hint logic should be in `js_config/node_version.ts`
- The old loose files (`js_config.ts`, `node_version.ts`) should be removed
- The old separate test file should be removed

### Inline Tests

The node version hint module should contain inline Vitest tests (tests written inside the source file, guarded by `if (import.meta.vitest)`). The inline tests should:

- Access vitest via `const { it, expect } = import.meta.vitest`
- Have test descriptions: `"detects supported TypeScript config specifiers"`, `"returns a node version hint for unsupported TypeScript module loading"`, `"does not add the hint for non-TypeScript specifiers or unrelated errors"`

### Configuration Updates

The following configuration changes are needed:

1. **package.json**: The test script should run `vitest run` (not vitest with `--dir` flag)
2. **tsconfig.json**: Should include `vitest/importMeta` in the `types` array under `compilerOptions`
3. **tsdown.config.ts**: Should define `import.meta.vitest` as `undefined` in the `define` section for bundling
4. **vitest.config.ts**: Should include `src-js/**/*.ts` in `includeSource` to run inline tests from source files

### Import Updates

The CLI entry point imports `loadJsConfig` from `./cli/js_config`. After reorganization, it should import from `./cli/js_config/index`.

## Verification

After making changes:

```bash
# TypeScript should compile without errors
npx tsc --noEmit

# Inline tests should run and pass
npx vitest run

# All original tests should still pass
pnpm test
```

## Guidance

- Vitest supports inline tests using `import.meta.vitest` guard — the test block only runs when vitest is executing
- When refactoring the error handling, focus on ensuring the caller always gets an `Error` with the hint in its message, not as a separate throw value
- Update the CLI import path to reflect the new directory structure
- Remove the old files after moving content to the new structure