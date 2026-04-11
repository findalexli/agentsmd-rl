# Add argument parsing, suite filtering, and grep support to integration test scripts

## Problem

The integration test scripts (`scripts/test-integration.sh` and `scripts/test-integration.bat`) have no way to filter which tests run. Running them always executes every integration test — all node.js integration tests plus every extension host test suite — which can take a very long time. There is no `--help` flag, no way to select specific extension test suites, and no way to grep for individual test cases by name across the different test runners.

Additionally, the `MOCHA_GREP` environment variable is not supported by several test runners (`test/integration/electron/testrunner.js`, `extensions/css-language-features/server/test/index.js`, `extensions/html-language-features/server/test/index.js`), so even manual attempts to filter tests by name don't work consistently.

## Expected Behavior

The integration test scripts should support:

- **`--run <file>`**: Run tests from a specific source file (node.js integration tests only)
- **`--runGlob <pattern>`** (aliases: `--glob`, `--runGrep`): Select test files by path glob
- **`--grep <pattern>`** (aliases: `-g`, `-f`): Filter test cases by name across all test runners
- **`--suite <pattern>`**: Select which extension host test suites to run (e.g., `git`, `api-folder`, `typescript`). Should support comma-separated lists. Node.js integration tests are skipped in this mode.
- **`--help`**: Show usage and list available suites
- Invalid `--suite` values should produce a clear error instead of silently running nothing

The grep pattern should be forwarded to extension host test runners via the `MOCHA_GREP` environment variable and `--grep` CLI flag as appropriate.

After implementing the code changes, update the relevant agent skills documentation to describe how to use the new integration test filtering capabilities. The existing `.github/skills/unit-tests/SKILL.md` already documents unit test running — there should be equivalent documentation for integration tests, and the unit test docs should cross-reference it.

## Files to Look At

- `scripts/test-integration.sh` — Main integration test runner (macOS/Linux)
- `scripts/test-integration.bat` — Windows equivalent
- `test/integration/electron/testrunner.js` — Electron-based test runner for node.js integration tests
- `extensions/css-language-features/server/test/index.js` — CSS extension test runner
- `extensions/html-language-features/server/test/index.js` — HTML extension test runner
- `.github/skills/` — Agent skills documentation directory
