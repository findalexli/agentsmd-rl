# Add `config` command to playwright-cli

## Problem

The `playwright-cli` terminal tool lets users manage browser sessions (open, close, session-list, etc.) but has no way to reconfigure a running session with a different config file. Users who want to change viewport, context options, or other config must manually stop and restart the session with new flags.

## Expected Behavior

A new `config` command should allow restarting the current session with a different configuration file. The command should:

1. Accept an optional path to a JSON config file (defaults to `playwright-cli.json`)
2. Stop the existing session if it's running, then reconnect with the new config
3. Work with named sessions via the `--session` flag
4. Be available as both `playwright-cli config <path>` and via `--config=<path>` with `open`

The daemon browser config should also set sensible default viewport dimensions (1280x720) for headless mode.

After implementing the code changes, update the project's skill documentation to reflect the new command and its usage patterns.

## Files to Look At

- `packages/playwright/src/mcp/terminal/command.ts` — Category type union for command grouping
- `packages/playwright/src/mcp/terminal/commands.ts` — Command declarations and the commands array
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — Help text categories and global options
- `packages/playwright/src/mcp/terminal/program.ts` — Session management and command routing
- `packages/playwright/src/mcp/browser/config.ts` — Daemon browser configuration defaults
- `packages/playwright/src/mcp/terminal/SKILL.md` — Skill documentation for the CLI tool
