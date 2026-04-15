# Split open/goto CLI commands and polish console output

## Problem

The `playwright-cli` tool currently combines browser opening and URL navigation into a single `open` command (e.g., `playwright-cli open https://example.com`). There is no way to open a browser without immediately navigating, and no dedicated `goto` command for subsequent navigation. This conflation makes the CLI less composable.

Additionally, the CLI's console output during `install` and workspace setup is plain and inconsistent — success and error messages lack visual distinction, and file paths are not formatted for readability.

## Expected Behavior

1. The CLI should support `open` (launch browser without a URL) and `goto` (navigate to a URL) as distinct operations, while still allowing `open https://...` as a shorthand.
2. Console output for the install flow should use emoji status prefixes — the Unicode character U+2705 (✅, "CHECK MARK") for success messages and U+274C (❌, "CROSS MARK") for error messages. File path references in output should be wrapped in literal backtick characters for clarity.
3. The project's skill documentation file should be updated to reflect the open/goto split, show `close` in usage examples, and fix the install command syntax.

## Files to Look At

- `packages/playwright/src/mcp/terminal/program.ts` — CLI command implementations, including `install` and workspace setup output
- `packages/playwright/src/skill/SKILL.md` — Skill documentation that agents and users read for CLI usage; must stay in sync with actual commands
- `tests/mcp/cli-misc.spec.ts` — Test expectations for CLI install output
