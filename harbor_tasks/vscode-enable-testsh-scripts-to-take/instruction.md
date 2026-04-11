# Enable bare file path arguments for test.sh

## Problem

The unit test runner (`test/unit/electron/index.js`) only accepts test files via the `--run <file>` flag. Agents and developers frequently try to pass file paths as bare positional arguments (e.g. `./scripts/test.sh src/vs/editor/test/common/model.test.ts`) but these are silently ignored, leading to all tests running instead of just the targeted file.

## Expected Behavior

The test runner should accept bare `.ts` and `.js` file paths as positional arguments and automatically treat them as `--run` values. Passing `./scripts/test.sh src/vs/editor/test/common/model.test.ts` should be equivalent to `./scripts/test.sh --run src/vs/editor/test/common/model.test.ts`. Multiple bare file paths should work too, and they should merge correctly with any explicit `--run` flags.

The help text should be updated to reflect this new usage.

After implementing the code change, update the relevant skill documentation to describe this new way of specifying test files so that agents can discover and use the feature.

## Files to Look At

- `test/unit/electron/index.js` — the Electron unit test entry point that parses CLI arguments
- `.github/skills/unit-tests/SKILL.md` — documents how to run unit tests, including CLI options
