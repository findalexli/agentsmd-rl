# Improve snap test runner usability

## Problem

The React Compiler's `snap` fixture test runner (`compiler/packages/snap/`) currently relies on a `testfilter.txt` file for filtering which fixtures to run and toggling debug mode. This is clunky — developers have to manually edit a text file to filter tests, and the `@debug` pragma parsing is fragile. The watch mode reads this file via a file watcher, which adds complexity.

The CLI interface should be modernized to use standard command-line flags instead:
- A `--pattern` (`-p`) string flag to filter fixtures by glob pattern (e.g., `yarn snap -p 'error.*'`)
- A `--debug` (`-d`) boolean flag to enable debug logging (print HIR for each compilation pass)
- In watch mode, interactive keyboard shortcuts: press `p` to type a filter pattern, `d` to toggle debug, `a` to run all tests

This means removing the `testfilter.txt` mechanism entirely: the `FILTER_FILENAME` and `FILTER_PATH` constants, the `readTestFilter()` function, and the file watcher subscription for the filter file.

## Expected Behavior

- `yarn snap -p 'use-memo'` runs only fixtures matching the pattern
- `yarn snap -d -p 'simple.js'` runs a single fixture with full debug HIR output
- `yarn snap -u` updates fixtures (existing behavior, keep working)
- In watch mode (`yarn snap -w`), pressing `p` enters pattern input mode, `d` toggles debug, `a` clears the filter
- The `testfilter.txt` file and all code referencing it are removed

After making the code changes, create a `compiler/CLAUDE.md` knowledge base document for the React Compiler. This should serve as a reference for AI agents working on the compiler, covering:
- Project structure (key packages and directories)
- How to run and filter tests using the updated snap commands
- Key compiler concepts (HIR, effects, etc.)
- Version control notes (this repo uses Sapling, not git)

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — exported constants including filter file paths
- `compiler/packages/snap/src/fixture-utils.ts` — `readTestFilter()` and `TestFilter` type
- `compiler/packages/snap/src/runner.ts` — CLI option parsing and main entry point
- `compiler/packages/snap/src/runner-watch.ts` — watch mode with keyboard handling and file watchers
