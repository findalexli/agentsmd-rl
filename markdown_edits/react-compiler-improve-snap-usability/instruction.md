# Improve snap CLI usability

## Problem

The React Compiler's snapshot test runner (`compiler/packages/snap`) uses a clunky `testfilter.txt` file for filtering which fixtures to run and enabling debug output. Developers must manually create/edit this file and use `@debug` pragmas inside it. In watch mode, the `f` key toggles reading from this file. This workflow is error-prone and not discoverable.

## What needs to change

Replace the `testfilter.txt`-based filtering mechanism with proper CLI flags:

1. **Remove the testfilter.txt mechanism entirely**: Remove the `FILTER_FILENAME` and `FILTER_PATH` constants, the `readTestFilter()` function, and all code that reads from or watches the testfilter file.

2. **Add a `--debug` / `-d` CLI flag**: A boolean flag that controls whether to emit debug information (HIR output for each compilation pass). In watch mode, this should be toggleable by pressing the `d` key.

3. **Add interactive pattern entry in watch mode**: Instead of watching a file, pressing `p` should let the user type a pattern directly. Pressing `a` should switch back to running all tests. The `--pattern` / `-p` flag (which already exists) should set the initial filter in watch mode.

4. **Update `runFixtures`**: The function should accept explicit `debug` and `requireSingleFixture` parameters instead of reading `filter.debug`.

After making the code changes, create a `compiler/CLAUDE.md` knowledge base document that covers:
- The compiler project structure (key packages and directories)
- How to run tests using the snap CLI (with the new `-p`, `-d`, `-u` flags)
- Version control notes (the repo uses Sapling)
- Key concepts like HIR, AliasingEffects, and the compilation pipeline

## Files to Look At

- `compiler/packages/snap/src/constants.ts` — defines shared constants including filter file paths
- `compiler/packages/snap/src/fixture-utils.ts` — contains `readTestFilter()` and `TestFilter` type
- `compiler/packages/snap/src/runner.ts` — main CLI entry point with yargs option definitions
- `compiler/packages/snap/src/runner-watch.ts` — watch mode with file subscriptions and key event handling
