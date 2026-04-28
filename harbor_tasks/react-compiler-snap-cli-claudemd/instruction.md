# Improve snap test runner usability

## Problem

The React Compiler's `snap` fixture test runner (`compiler/packages/snap/`) currently relies on a `testfilter.txt` file for filtering which fixtures to run and toggling debug mode. This is clunky — developers have to manually edit a text file to filter tests, and the `@debug` pragma parsing is fragile. The watch mode reads this file via a file watcher, which adds complexity.

The CLI interface should be modernized to use standard command-line flags instead of the file-based mechanism.

## Expected Behavior

### CLI Flags

The CLI is built with yargs. It should support the following options:
- `--debug` / `-d`: A boolean flag to enable debug logging (print HIR for each compilation pass)
- `--pattern` / `-p`: A string flag to filter fixtures by glob pattern (e.g., `yarn snap -p 'error.*'`)
- `--update` / `-u`: Keep existing behavior (existing flag)

Remove the old `--filter` boolean option and any imports related to the file-based filter mechanism.

### Watch Mode

In watch mode (`yarn snap -w`), the runner should support interactive keyboard input:
- Press `p` to enter pattern input mode and type a filter pattern
- Press `d` to toggle debug mode
- Press `a` to clear filter and run all tests

The watch runner needs internal state to track:
- Whether the user is currently typing a pattern
- The accumulated pattern characters being typed

Update the watch runner initialization to accept parameters for debug mode and initial pattern from the CLI flags. Remove all usage of the file-based filter reading mechanism.

### Expected Usage

- `yarn snap -p 'use-memo'` runs only fixtures matching the pattern
- `yarn snap -d -p 'simple.js'` runs a single fixture with full debug HIR output
- `yarn snap -u` updates fixtures (existing behavior, keep working)
- In watch mode (`yarn snap -w`), press `p` to type a pattern, `d` to toggle debug, `a` to clear filter

### Cleanup

Remove the file-based filter mechanism:
- Remove `FILTER_FILENAME` and `FILTER_PATH` constants from `constants.ts`
- Remove the `readTestFilter` function from `fixture-utils.ts`
- Remove the `subscribeFilterFile` file watcher subscription from watch mode

### CLAUDE.md Knowledge Base

After making the code changes, create a `compiler/CLAUDE.md` knowledge base document for the React Compiler. This should serve as a reference for AI agents working on the compiler, covering at minimum:
- Project structure — mention `babel-plugin-react-compiler` as a key package
- How to run and filter tests using the updated snap commands (document `yarn snap`, the `-p`/`--pattern` flag, `-d`/`--debug` flag, and `-u` flag)
- Key compiler concepts including **HIR** (High-level Intermediate Representation)
- Test fixtures

The document should be substantive (at least 200 characters).

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — exported constants including filter file paths
- `compiler/packages/snap/src/fixture-utils.ts` — filter reading function and type
- `compiler/packages/snap/src/runner.ts` — CLI option parsing and main entry point
- `compiler/packages/snap/src/runner-watch.ts` — watch mode with keyboard handling and file watchers

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
