# Add a `kill-all` CLI command for daemon processes

## Problem

When Playwright CLI daemon processes become stale or unresponsive (zombie processes), users have no way to forcefully terminate them. The existing `session-stop-all` command performs a graceful shutdown but doesn't help when daemons are stuck and won't respond to normal stop signals.

## Expected Behavior

A new `kill-all` CLI command should:
1. Find all running daemon processes (those started with `run-mcp-server` and `--daemon-session`)
2. Forcefully kill them with `SIGKILL` (or equivalent on Windows)
3. Report how many processes were killed, or indicate none were found

The command should work cross-platform (Linux/macOS via `ps aux`, Windows via PowerShell).

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — command declarations and registry
- `packages/playwright/src/mcp/terminal/program.ts` — command routing and implementation
- `packages/playwright/src/skill/SKILL.md` — CLI command documentation (update after implementing)
- `packages/playwright/src/skill/references/session-management.md` — session management reference docs
- `.claude/skills/playwright-mcp-dev/SKILL.md` — development instructions for adding CLI commands

After implementing the command, update the relevant skill documentation and references to include the new `kill-all` command. The project's development guidelines require documentation updates when adding new CLI commands.
