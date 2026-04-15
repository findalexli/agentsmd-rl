# Vendor and simplify minimist as TypeScript

## Problem

The CLI client in `packages/playwright-core/src/tools/cli-client/` currently depends on the external `minimist` npm package for command-line argument parsing (`require('minimist')`). This introduces an unnecessary external dependency when the actual usage is simple enough to vendor directly.

Additionally, the current code in `program.ts` has significant post-processing logic after calling minimist: it manually converts all values to strings, removes unspecified boolean options (to avoid default `false`), and detects `--bool=value` usage to emit errors. This post-processing should be integrated into the parser itself.

## Expected Behavior

1. **Create a vendored minimist implementation** as a new file `minimist.ts` in the cli-client directory (`packages/playwright-core/src/tools/cli-client/minimist.ts`). The module must:
   - Export a named function called `minimist` that accepts `(args: string[], opts?)` and returns parsed arguments
   - Export a `MinimistArgs` type with `_` (string array for positional args) and an index signature for string/boolean options
   - Parse `--key value`, `--key=value`, `--no-key`, `-f` short flags, and positional args
   - Accept `boolean` and `string` option declarations
   - NOT assign default `false` to unspecified boolean options
   - Throw an error when a boolean option is passed with `=value` (e.g. `--verbose=true`). The error message must include the option name so users know which flag caused the issue
   - Handle the `--` separator: all arguments after `--` must be treated as positional (stored in `_`), not parsed as flags

2. **Update program.ts** to import the `minimist` function and `MinimistArgs` type from the local `'./minimist'` path, replacing the `require('minimist')` call and the local `MinimistArgs` type definition. The file must contain an import using `from './minimist'` and must no longer contain `require('minimist')`.

3. **Update session.ts** to import the `MinimistArgs` type from `'./minimist'`, replacing the local type definition.

4. **Update DEPS.list** in the cli-client directory. The DEPS.list uses a section-based format where each section header is a filename in square brackets (e.g. `[program.ts]`, `[session.ts]`) followed by its allowed imports listed one per line. You must:
   - Add the literal string `./minimist.ts` as an allowed import entry under the sections for files that import from it (e.g. `[program.ts]` and `[session.ts]`)
   - Add a new section with the header `[minimist.ts]` containing `"strict"` as its declaration

5. **Remove `@types/minimist`** from devDependencies in `package.json` since the vendored module provides its own types.

6. **Update CLAUDE.md** in the commit message conventions section to add a rule that includes the phrase "Generated with" — specifically, a rule stating never to add that phrase in commit messages.

## Files to Look At

- `packages/playwright-core/src/tools/cli-client/program.ts` — main CLI entry point, currently uses `require('minimist')`
- `packages/playwright-core/src/tools/cli-client/session.ts` — session management, has its own local `MinimistArgs` type
- `packages/playwright-core/src/tools/cli-client/DEPS.list` — import boundary declarations for the cli-client module
- `CLAUDE.md` — project-level agent instructions, including commit conventions
