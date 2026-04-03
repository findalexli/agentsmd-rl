# Add compile subcommand and fix path resolution in snap tool

## Problem

The React Compiler's `snap` test runner (`compiler/packages/snap/`) has two issues:

1. **No way to compile arbitrary files.** Currently you can only run `snap` against test fixtures. There's no subcommand to compile a standalone file to see the React Compiler output, which makes debugging harder when you don't have a fixture yet.

2. **Broken relative path resolution.** The `minimize` command resolves relative paths from `process.cwd()` (the snap package directory), but users run `yarn snap` from the `compiler/` directory. Paths like `packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/foo.js` don't resolve correctly.

The root cause of the path issue is that `PROJECT_ROOT` in `constants.ts` currently points directly to `babel-plugin-react-compiler`, conflating two different concepts: the compiler project root (the `compiler/` directory from which users invoke commands) and the babel plugin package root.

## Expected Behavior

1. A new `yarn snap compile <path>` command that compiles any file with the React Compiler and prints the output. It should support a `--debug` flag to show the state after each compiler pass (similar to `yarn snap -d -p <pattern>` but for arbitrary files).

2. The `minimize` command should accept `<path>` as a positional argument (currently it uses `--path`/`-p`), consistent with the new `compile` command.

3. Both `compile` and `minimize` should resolve relative paths from the compiler project root (two directories up from the snap package), not from `process.cwd()`.

4. The internal constants should clearly separate the compiler project root from the babel-plugin-react-compiler package path, since other files (runner-watch, runner-worker, minimize) also depend on these paths for different purposes (building vs running fixtures).

After implementing the code changes, update the project documentation (`compiler/CLAUDE.md` and `compiler/docs/DEVELOPMENT_GUIDE.md`) to document the new `compile` command and the `minimize` positional path syntax, so that developers and agents can discover and use these tools.

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — path constant definitions
- `compiler/packages/snap/src/runner.ts` — CLI entry point with yargs command registration
- `compiler/packages/snap/src/minimize.ts` — minimize command implementation
- `compiler/packages/snap/src/runner-watch.ts` — watch mode (uses path constants)
- `compiler/packages/snap/src/runner-worker.ts` — test worker (uses path constants)
- `compiler/CLAUDE.md` — agent instructions for the compiler
- `compiler/docs/DEVELOPMENT_GUIDE.md` — developer guide
