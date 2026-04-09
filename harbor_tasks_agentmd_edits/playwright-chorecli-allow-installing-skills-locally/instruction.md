# chore(cli): allow installing skills locally

## Problem

The Playwright CLI currently lacks a command to install skill files to the local workspace. Users need a way to copy the SKILL.md documentation and reference files from the playwright package to their local `.claude/skills/playwright/` directory for integration with Claude and GitHub Copilot.

Additionally, there are several related issues:

1. The `install` command is ambiguously named - it only installs browsers, but its name suggests broader functionality
2. The route tools (`browser_route`, `browser_route_list`, `browser_unroute`) are categorized under `core` capability, but they should be under a new `network` capability since they deal with network request interception
3. The `--isolated` flag has been renamed to `--in-memory` for clarity, but the help text hasn't been updated

## Expected Behavior

After the fix:

1. A new `install-skills` CLI command exists that copies skill files from `packages/playwright/src/skill/` to `.claude/skills/playwright/` in the current working directory
2. The existing `install` command is renamed to `install-browser` for clarity
3. Route tools use the `network` capability instead of `core`
4. The `network` capability is added to the config type definitions
5. The help text shows `--in-memory` instead of `--isolated`

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` - Where CLI commands are defined. Need to add `installSkills` command and rename `install` to `install-browser`
- `packages/playwright/src/mcp/terminal/program.ts` - Where command execution is handled. Need to add `installSkills()` function implementation
- `packages/playwright/src/mcp/browser/tools/route.ts` - Where route tools are defined. Need to change capability from `core` to `network`
- `packages/playwright/src/mcp/config.d.ts` - Where tool capabilities are typed. Need to add `'network'` type
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` - Where help text is generated. Need to update `--isolated` to `--in-memory`
- `.claude/skills/playwright-mcp-dev/SKILL.md` - Documentation for MCP dev skill. Need to document the skill file location

## Implementation Notes

The `installSkills()` function should:
1. Source directory: `packages/playwright/src/skill/` (relative to the CLI location)
2. Destination: `.claude/skills/playwright/` in current working directory
3. Use `fs.promises.cp()` with `recursive: true` to copy all files
4. Print success message with the relative path to the destination

The function should handle errors gracefully - if the source directory doesn't exist, exit with code 1 and an error message.
