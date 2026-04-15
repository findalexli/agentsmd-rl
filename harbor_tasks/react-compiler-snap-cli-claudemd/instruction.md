# Improve snap test runner usability

## Problem

The React Compiler's `snap` fixture test runner (`compiler/packages/snap/`) currently relies on a `testfilter.txt` file for filtering which fixtures to run and toggling debug mode. This is clunky — developers have to manually edit a text file to filter tests, and the `@debug` pragma parsing is fragile. The watch mode reads this file via a file watcher, which adds complexity.

The CLI interface should be modernized to use standard command-line flags instead:
- A `--pattern` (`-p`) string flag to filter fixtures by glob pattern (e.g., `yarn snap -p 'error.*'`)
- A `--debug` (`-d`) boolean flag to enable debug logging (print HIR for each compilation pass)
- In watch mode, interactive keyboard shortcuts: press `p` to type a filter pattern, `d` to toggle debug, `a` to run all tests

This means removing the `testfilter.txt` mechanism entirely: the `FILTER_FILENAME` and `FILTER_PATH` constants, the `readTestFilter()` function, the `subscribeFilterFile` function, and the file watcher subscription for the filter file.

## Expected Behavior

### CLI Flags (yargs)

The CLI is built with yargs. Define the options using the yargs builder API:
- `--debug` / `-d`: Register as `.boolean('debug')` with short alias via `.alias('d', 'debug')`.
- `--pattern` / `-p`: A string option for glob-based fixture filtering.
- `--update` / `-u`: Keep existing behavior.

Remove the old `--filter` boolean option from runner.ts, along with any imports of `readTestFilter` and `FILTER_PATH`.

### Watch Mode

In `runner-watch.ts`, update the `makeWatchRunner` function signature to accept:
- `debugMode: boolean` — whether debug output is enabled
- `initialPattern` (optional string) — initial glob pattern from the CLI `-p` flag

Remove any usage of `readTestFilter` from this file.

The watch mode needs an interactive state machine for keyboard input. The `RunnerState` type should include:
- `inputMode` — tracks whether the user is currently typing a pattern
- `inputBuffer` — accumulates the typed pattern characters

Key handlers (via `key.name`):
- `'p'` — enter pattern input mode
- `'d'` — toggle debug mode
- `'a'` — clear filter and run all tests

Remove the `subscribeFilterFile` function entirely.

### Expected Usage

- `yarn snap -p 'use-memo'` runs only fixtures matching the pattern
- `yarn snap -d -p 'simple.js'` runs a single fixture with full debug HIR output
- `yarn snap -u` updates fixtures (existing behavior, keep working)
- In watch mode (`yarn snap -w`), pressing `p` enters pattern input mode, `d` toggles debug, `a` clears the filter

### Cleanup

Remove from `constants.ts`:
- `FILTER_FILENAME` export
- `FILTER_PATH` export
- `testfilter.txt` reference

Remove from `fixture-utils.ts`:
- `readTestFilter` function
- `TestFilter` type's `debug` property

### CLAUDE.md Knowledge Base

After making the code changes, create a `compiler/CLAUDE.md` knowledge base document for the React Compiler. This should serve as a reference for AI agents working on the compiler, covering at minimum:
- Project structure — mention `babel-plugin-react-compiler` as a key package
- How to run and filter tests using the updated snap commands (document `yarn snap`, the `-p`/`--pattern` flag, `-d`/`--debug` flag, and `-u` flag)
- Key compiler concepts including **HIR** (High-level Intermediate Representation)
- Test fixtures

The document should be substantive (at least 200 characters).

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — exported constants including filter file paths
- `compiler/packages/snap/src/fixture-utils.ts` — `readTestFilter()` and `TestFilter` type
- `compiler/packages/snap/src/runner.ts` — CLI option parsing and main entry point
- `compiler/packages/snap/src/runner-watch.ts` — watch mode with keyboard handling and file watchers
