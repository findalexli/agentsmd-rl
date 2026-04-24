# Vendor minimist as a local TypeScript module in the Playwright CLI client

## Problem

The Playwright CLI client at `packages/playwright-core/src/tools/cli-client/` uses the external `minimist` npm package for command-line argument parsing. There are issues with how the external package integrates with the TypeScript types in this codebase: boolean options that are not explicitly passed are incorrectly defaulting to `false`, and boolean options passed with `=value` are not handled correctly. The two main source files each define their own local `MinimistArgs` type rather than sharing one.

Replace the external dependency with a local, vendored TypeScript implementation that handles all the required parsing behavior correctly.

## Requirements

### Parser behavior

The vendored module should export a `minimist` function and a `MinimistArgs` type (with `_` as a string array for positional args and an index signature for string/boolean options). The parser must support:

- `--key value` and `--key=value` long options
- `--no-key` negation (sets the key to `false`)
- `-f` short flags
- Positional arguments collected in `_`
- `boolean` and `string` option type declarations
- Boolean options that are not explicitly passed should **not** default to `false`
- If a boolean option is passed with `=value` (e.g. `--verbose=true`), the parser must throw an error whose message includes the option name
- The `--` separator: everything after `--` must be treated as positional, not parsed as flags

### Integration

- `program.ts` should import `minimist` and `MinimistArgs` from the local `'./minimist'` module.
- `session.ts` should use the shared `MinimistArgs` type from the local module rather than defining its own copy.
- The `@types/minimist` entry in `devDependencies` of the root `package.json` is no longer needed once the vendored module provides its own TypeScript types.

### Project conventions

- **DEPS.list**: The cli-client directory uses a `DEPS.list` file to declare allowed imports per source file. Sections are headed by filenames in brackets (e.g. `[program.ts]`, `[session.ts]`). The new module must be registered: files that import from it need `./minimist.ts` as an allowed import in their section, and the new module itself needs its own section (`[minimist.ts]`) declaring `"strict"` mode.
- **CLAUDE.md**: The project's `CLAUDE.md` documents commit message conventions. It should include a rule that commit messages must never contain the phrase "Generated with".

## Relevant files

- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI entry point, uses external minimist
- `packages/playwright-core/src/tools/cli-client/session.ts` — session management, defines its own `MinimistArgs` type
- `packages/playwright-core/src/tools/cli-client/DEPS.list` — import boundary declarations
- `package.json` — root package, contains `@types/minimist` in devDependencies
- `CLAUDE.md` — project-level conventions including commit message rules

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
