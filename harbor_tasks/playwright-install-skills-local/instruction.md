# Add install-skills command and reorganize route capabilities

## Problem

The Playwright CLI has several issues with its command organization:

1. The `install` command name is ambiguous — it only installs browsers, but the generic name doesn't convey that. It should be renamed to `install-browser`.

2. There's no way for users to install the Claude/Copilot skill files to their local workspace. A new `install-skills` command is needed that copies the skill files from the package source directory (`packages/playwright/src/skill/`) into the user's local `.claude/skills/playwright/` directory, including the `SKILL.md` and the `references/` subdirectory.

3. The route-related MCP tools (`browser_route`, `browser_route_list`, `browser_unroute`) are grouped under the `core` capability, but they logically belong to a separate `network` capability. A new `network` capability should be added to the type definitions, and the route tools should be moved to it.

## Expected Behavior

- Running `install-browser` installs browsers (same as old `install` command)
- Running `install-skills` copies the skill directory to `.claude/skills/playwright/`
- Route tools are registered under the `network` capability
- The `ToolCapability` type in `config.d.ts` includes `'network'`
- Skill documentation is updated to reflect all new commands and capability organization

## Required Documentation Updates

The skill documentation at `packages/playwright/src/skill/SKILL.md` must be updated to include:

1. A `### Network` section (or `## Network` at the top level) documenting the route commands
2. The `route-list` and `unroute` CLI command names in that section
3. An `### Install` section documenting `install-browser` and `install-skills` commands

Additionally, `packages/playwright/src/skill/references/request-mocking.md` must document the direct CLI route commands:
- `playwright-cli route-list`
- `playwright-cli unroute`

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations
- `packages/playwright/src/mcp/terminal/program.ts` — CLI command handlers and dispatch
- `packages/playwright/src/mcp/browser/tools/route.ts` — Route tool definitions with capability assignment
- `packages/playwright/src/mcp/config.d.ts` — ToolCapability type definition
- `packages/playwright/src/skill/SKILL.md` — Skill file documenting all CLI commands (must be updated to reflect changes)
- `packages/playwright/src/skill/references/request-mocking.md` — Request mocking reference documentation

## Important

After making the code changes, the skill documentation files must be updated to reflect the new commands and capability reorganization. Check the project's agent instructions for guidance on when skill docs should be updated.
