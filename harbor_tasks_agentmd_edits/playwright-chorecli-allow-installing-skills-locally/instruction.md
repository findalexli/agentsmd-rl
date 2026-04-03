# Add local skill installation and reorganize CLI commands

## Problem

The Playwright CLI currently bundles all route-related MCP tools (browser_route, browser_route_list, browser_unroute) under the `core` capability, making it impossible to selectively enable network-related tools. The `install` command name is ambiguous — it installs browsers but doesn't make that clear. There is no way to install the Playwright skill files (SKILL.md and references) into a local workspace for use with Claude or GitHub Copilot.

Additionally, the help text still references the old `--isolated` flag name instead of the current `--in-memory`.

## Expected Behavior

1. **Route tools should use a dedicated `network` capability** — Add `'network'` to the `ToolCapability` type and update all three route tool definitions to use it.

2. **Rename `install` to `install-browser`** — Make it clear the command installs browsers.

3. **Add `install-skills` command** — A new CLI command that copies the skill directory (`packages/playwright/src/skill/`) into the user's workspace at `.claude/skills/playwright/`, enabling local access to skill documentation.

4. **Fix help text** — Replace `--isolated` with `--in-memory` in the help generator.

After making the code changes, update the relevant skill documentation files to reflect the new commands and capabilities. The project's skill file at `packages/playwright/src/skill/SKILL.md` should document the new Network and Install command sections. The developer skill file at `.claude/skills/playwright-mcp-dev/SKILL.md` should also be updated to help future contributors know where the skill file lives and when to update it.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/route.ts` — route tool definitions with capability field
- `packages/playwright/src/mcp/config.d.ts` — ToolCapability type definition
- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations
- `packages/playwright/src/mcp/terminal/program.ts` — CLI command execution logic
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — CLI help text generation
- `packages/playwright/src/skill/SKILL.md` — user-facing skill documentation
- `.claude/skills/playwright-mcp-dev/SKILL.md` — developer skill documentation
