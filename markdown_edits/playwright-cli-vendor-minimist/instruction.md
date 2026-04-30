# Task: Vendor minimist as TypeScript for CLI Client

## Overview

The Playwright CLI client currently depends on the external `minimist` npm package for command-line argument parsing. This dependency needs to be replaced with a custom TypeScript implementation that is vendored directly in the codebase.

## Primary Task

Create a TypeScript implementation of a minimal argument parser in `packages/playwright-core/src/tools/cli-client/minimist.ts` that:

1. **Parses boolean arguments**: `--verbose`, `--no-debug` should set `verbose=true`, `debug=false`
2. **Parses string arguments**: `--name value` or `--name=value` should set `name=value`
3. **Handles positional arguments**: Arguments after `--` or non-flag args go into `_` array
4. **Enforces boolean semantics**: Throw an error if a boolean flag is passed with `=value` (e.g., `--verbose=true`)
5. **Supports short flags**: Single-letter flags like `-v` should work
6. **Provides TypeScript types**: Export `MinimistOptions`, `MinimistArgs` interfaces

## Integration Changes

After creating the minimist module, update the existing CLI client code:

1. **program.ts**: Replace the `require('minimist')` call with an import from the local `./minimist` module. Update type references.
2. **session.ts**: Import the `MinimistArgs` type from the local module instead of defining it locally.
3. **DEPS.list**: Add the new `minimist.ts` file to the dependency declarations for both `program.ts` and `session.ts`.

## Config/Documentation Update

The project maintains commit message conventions in `CLAUDE.md`. You need to add a new rule to the existing commit conventions section:

- The conventions are documented near the "Commit Convention" heading
- Add a rule about avoiding "Generated with" text in commit messages
- Follow the existing format of the other convention entries

## Files to Modify

- **Create**: `packages/playwright-core/src/tools/cli-client/minimist.ts`
- **Modify**: `packages/playwright-core/src/tools/cli-client/program.ts`
- **Modify**: `packages/playwright-core/src/tools/cli-client/session.ts`
- **Modify**: `packages/playwright-core/src/tools/cli-client/DEPS.list`
- **Modify**: `CLAUDE.md` (add commit convention rule)

## Notes

- The vendored implementation should include proper MIT license attribution to the original minimist author (James Halliday)
- Keep the implementation minimal - only implement features actually used by the CLI client
- The DEPS system enforces import boundaries; files marked `"strict"` can only import explicitly declared dependencies
- Review `CLAUDE.md` for the project's commit message conventions before updating
