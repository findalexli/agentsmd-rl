# Add install-skills command and reorganize route capabilities

## Problem

The Playwright CLI has several issues with its command organization:

1. The `install` command name is ambiguous — it only installs browsers, but the generic name doesn't convey that. It should be renamed to `install-browser`.

2. There's no way for users to install the Claude/Copilot skill files to their local workspace. A new `install-skills` command is needed that copies the skill files from the package source directory into the user's local `.claude/skills/playwright/` directory.

3. The route-related MCP tools (`browser_route`, `browser_route_list`, `browser_unroute`) are grouped under the `core` capability, but they logically belong under a separate `network` capability.

## Required Code Changes

### Command Changes
- Rename the `install` command to `install-browser`
- Add a new `install-skills` command that copies skill files from the package source to `.claude/skills/playwright/`

### Capability Changes
- Add `network` to the ToolCapability type definition
- Move the three route tools to use the `network` capability instead of `core`

## Required Documentation Updates

### SKILL.md Updates
The skill documentation must include:

1. A `### Network` section (or `## Network` at the top level) containing the literal strings:
   - `route-list`
   - `unroute`

2. An `### Install` section containing the literal strings:
   - `install-browser`
   - `install-skills`

### request-mocking.md Updates
The request mocking reference documentation must document the direct CLI route commands by including these literal strings:
- `playwright-cli route-list`
- `playwright-cli unroute`

## Expected Behavior

- Running `install-browser` installs browsers (same as old `install` command)
- Running `install-skills` copies the skill directory to `.claude/skills/playwright/`
- Route tools are registered under the `network` capability
- The `ToolCapability` type includes `'network'`
- SKILL.md documents the Network capability with route-list and unroute commands
- SKILL.md documents the Install section with install-browser and install-skills commands
- request-mocking.md documents the direct CLI commands `playwright-cli route-list` and `playwright-cli unroute`
