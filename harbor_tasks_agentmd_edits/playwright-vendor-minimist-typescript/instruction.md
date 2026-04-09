# Vendor and simplify minimist as TypeScript

## Problem

The CLI client in `packages/playwright-core/src/tools/cli-client/` currently depends on the external `minimist` npm package for command-line argument parsing (`require('minimist')`). This introduces an unnecessary external dependency when the actual usage is simple enough to vendor directly.

Additionally, the current code in `program.ts` has significant post-processing logic after calling minimist: it manually converts all values to strings, removes unspecified boolean options (to avoid default `false`), and detects `--bool=value` usage to emit errors. This post-processing should be integrated into the parser itself.

## Expected Behavior

1. **Create a vendored minimist implementation** as a TypeScript file in the cli-client directory that:
   - Parses `--key value`, `--key=value`, `--no-key`, `-f` short flags, and positional args
   - Accepts `boolean` and `string` option declarations
   - Does NOT assign default `false` to unspecified boolean options
   - Throws an error when a boolean option is passed with `=value` (e.g. `--verbose=true`)
   - Handles the `--` separator for pass-through arguments

2. **Update program.ts and session.ts** to import from the vendored file instead of using `require('minimist')`. Share the `MinimistArgs` type from the vendored module rather than defining it locally in each file.

3. **Remove `@types/minimist`** from devDependencies in `package.json` since the vendored module provides its own types.

4. After making the code changes, update the project's agent instruction file to reflect current commit message conventions. The existing commit rules section should be extended to cover additional patterns that automated tools may add.

## Files to Look At

- `packages/playwright-core/src/tools/cli-client/program.ts` — main CLI entry point, currently uses `require('minimist')`
- `packages/playwright-core/src/tools/cli-client/session.ts` — session management, has its own local `MinimistArgs` type
- `packages/playwright-core/src/tools/cli-client/DEPS.list` — import boundary declarations for the cli-client module
- `CLAUDE.md` — project-level agent instructions, including commit conventions
