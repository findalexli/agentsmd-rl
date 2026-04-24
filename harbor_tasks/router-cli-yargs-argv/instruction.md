# Fix TanStack Router CLI Silent Failure

The router CLI (`@tanstack/router-cli`) is failing silently - commands are not being recognized or processed.

## Symptoms

When you run CLI commands like `tsr --help`, `tsr generate`, or `tsr watch`, the CLI exits without any output and without doing anything. No error message, no help text, nothing.

## Relevant Files

- `packages/router-cli/src/index.ts` - The CLI entry point where yargs is configured

## Context

The CLI uses `yargs` for argument parsing. The current implementation creates a yargs instance but doesn't appear to be receiving or processing command-line arguments. The yargs setup includes commands for `generate` and `watch`, but they're never invoked.

When running the CLI with `--help`, you should see usage information with the available commands. When running with `generate` or `watch`, you should see either successful execution or an error about missing configuration - not complete silence.

## Expected Behavior

- `tsr --help` should display help text with available commands
- `tsr generate` should attempt to generate routes (may fail without config, but should not be silent)
- `tsr watch` should attempt to watch for changes (may fail without config, but should not be silent)

## yargs Configuration

The yargs library requires its arguments to be passed explicitly. The `hideBin` function from `yargs/helpers` strips the node path and script path from `process.argv` before passing the remaining arguments to yargs. Without this step, yargs receives an empty argument list and produces no output.

Your fix should ensure yargs receives the CLI arguments properly, for example using the pattern `yargs(hideBin(process.argv))`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
