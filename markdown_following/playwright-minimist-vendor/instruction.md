# Task: Vendor minimist as TypeScript and Update CLAUDE.md

## Problem

The CLI client tools in `packages/playwright-core/src/tools/cli-client/` depend on the external `minimist` npm package. This external dependency needs to be replaced with a vendored TypeScript implementation.

Currently, `program.ts` and `session.ts` define their own local `MinimistArgs` types and use `require('minimist')` to import the external package. Additionally, `program.ts` contains validation logic that manually checks if boolean options are passed with `=value` syntax and exits with an error. This validation should be handled by the vendored implementation instead.

## Requirements

### Part 1: Vendored minimist Implementation

Create a new file `packages/playwright-core/src/tools/cli-client/minimist.ts` that exports:

1. **`MinimistOptions` interface** with optional `string` and `boolean` properties
2. **`MinimistArgs` interface** with:
   - `_` property (string array for positional arguments)
   - Index signature for option values (`[key: string]: string | boolean | string[] | undefined`)
3. **`minimist` function** with signature `minimist(args: string[], opts?: MinimistOptions): MinimistArgs`

The implementation must:
- Parse `--option=value` syntax for string options
- Parse `--no-option` syntax for boolean negation
- Collect positional arguments in the `_` array
- **Throw an error containing the text `should not be passed with '=value'` when a boolean option is passed with `=value` format (e.g., `--bool=true`)**

Update `packages/playwright-core/src/tools/cli-client/program.ts`:
- **Import `minimist` from `./minimist`** (local module, not external package)
- **Import `MinimistArgs` type from `./minimist`**
- Remove the local `MinimistArgs` type definition
- Remove `require('minimist')` usage
- Remove the manual boolean validation logic that checks for `=value` syntax

Update `packages/playwright-core/src/tools/cli-client/session.ts`:
- **Import `MinimistArgs` type from `./minimist`**
- Remove the local `MinimistArgs` type definition

Update `packages/playwright-core/src/tools/cli-client/DEPS.list`:
- Add `./minimist.ts` as a dependency for `program.ts`
- Add `./minimist.ts` as a dependency for `session.ts`
- Add a `[minimist.ts]` section with a `"strict"` marker

Update `package.json`:
- Remove `@types/minimist` from devDependencies

Run `npm install` to update `package-lock.json`.

### Part 2: CLAUDE.md Update

In `CLAUDE.md`, add a new rule in the Commit Convention section with the following text:

```
Never add "Generated with" in commit message.
```

### Verification

- `npx tsc --noEmit` must pass without errors
- The CLI client tools must parse arguments correctly
- DEPS.list must be correctly updated for the dependency check
