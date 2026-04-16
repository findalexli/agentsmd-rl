# Vendor minimist as TypeScript

## Problem

The CLI client in `packages/playwright-core/src/tools/cli-client/` currently depends on the external `minimist` npm package for argument parsing. We need to vendor this dependency as an internal TypeScript module to reduce external dependencies and enable better type safety.

## Requirements

1. **Create vendored minimist module**: Create `packages/playwright-core/src/tools/cli-client/minimist.ts` with:
   - `MinimistOptions` interface for configuration (string[], boolean[] options)
   - `MinimistArgs` interface for return type (`_: string[]` plus key-value pairs)
   - `minimist(args: string[], opts?): MinimistArgs` function
   - Support for:
     - Boolean flags (`--help`, `--no-headless`)
     - String options (`--name value`)
     - Shorthand flags (`-abc`)
     - Positional arguments
     - Error on boolean flags with `=value` syntax (throw error message)
   - Strip unused features: aliases, defaults, stopEarly, dot-notation keys

2. **Update program.ts**: Modify `packages/playwright-core/src/tools/cli-client/program.ts` to:
   - Import `minimist` from the new local module instead of using `require('minimist')`
   - Import `MinimistArgs` type from the new module
   - Remove the local `MinimistArgs` type definition
   - Remove the manual boolean post-processing code
   - Handle type assertions for `args.session` and `args.all` where needed

3. **Update session.ts**: Modify `packages/playwright-core/src/tools/cli-client/session.ts` to:
   - Import `MinimistArgs` type from the new local module
   - Remove the local `MinimistArgs` type definition
   - Handle type assertions for `cliArgs.session`

4. **Update DEPS.list**: Add `./minimist.ts` as a dependency for `[program.ts]` and `[session.ts]`, and create a `[minimist.ts]` section marked as `"strict"`

5. **Update CLAUDE.md**: Add a new commit convention rule after the existing "Never add Co-Authored-By agents" rule: `Never add "Generated with" in commit message.`

6. **Update package.json**: Remove the `@types/minimist` dev dependency

The vendored implementation should match the actual usage patterns in the CLI client - refer to how arguments are currently being parsed in program.ts to understand what features are needed.
