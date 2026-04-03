# Snap CLI: Add compile subcommand and fix path resolution

## Problem

The React Compiler's `snap` test runner (`compiler/packages/snap/`) has two usability issues:

1. **No way to compile arbitrary files.** Currently, `yarn snap` only runs compilation on fixture files under `__tests__/fixtures/`. If you want to quickly compile a standalone `.js` or `.ts` file to see the React Compiler output, you have to first copy it into the fixtures directory and run it through the test harness. There should be a `yarn snap compile <path>` command that compiles any file directly and prints the output, with an optional `--debug` flag to show the state after each compiler pass.

2. **Relative path resolution is wrong.** The `yarn snap minimize` command (and the new compile command) resolves relative paths from `process.cwd()`, which is the snap package directory (`compiler/packages/snap/`). But developers invoke `yarn snap` from the `compiler/` directory, so paths like `packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/foo.js` don't resolve correctly. Relative paths should resolve from the compiler root directory instead.

3. **Inconsistent CLI interface.** The `minimize` command takes its path via `--path` / `-p` flag, but it would be more natural and consistent with the new `compile` command to accept the path as a positional argument: `yarn snap minimize <path>`.

Additionally, the constant names in `compiler/packages/snap/src/constants.ts` are misleading: `PROJECT_ROOT` actually points to the `babel-plugin-react-compiler` package, not the project root. These should be renamed to reflect what they actually reference.

## Expected Behavior

- `yarn snap compile <path>` compiles the given file and prints the compiled output
- `yarn snap compile --debug <path>` shows the state after each compiler pass
- `yarn snap minimize <path>` works with path as a positional argument
- Relative paths in both commands resolve from the `compiler/` directory
- Constants in `constants.ts` are named accurately (`BABEL_PLUGIN_ROOT`, `BABEL_PLUGIN_SRC`)
- All files importing the old constant names are updated

After making the code changes, update the project's developer documentation to cover the new and updated commands. The `compiler/CLAUDE.md` and `compiler/docs/DEVELOPMENT_GUIDE.md` should document how to use `yarn snap compile` and `yarn snap minimize`.

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — exports path constants used across snap
- `compiler/packages/snap/src/runner.ts` — yargs CLI setup and command handlers
- `compiler/packages/snap/src/minimize.ts` — minimize command implementation
- `compiler/packages/snap/src/runner-worker.ts` — test worker that imports compiler constants
- `compiler/packages/snap/src/runner-watch.ts` — file watcher that uses project path constants
- `compiler/CLAUDE.md` — agent knowledge base for the React Compiler
- `compiler/docs/DEVELOPMENT_GUIDE.md` — developer guide for compiler contributors
