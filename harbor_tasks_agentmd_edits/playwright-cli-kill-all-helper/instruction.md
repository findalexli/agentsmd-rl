Add a `kill-all` CLI command to forcefully terminate any stale or zombie MCP daemon processes.

## Background

The Playwright CLI has session management commands (`session-stop`, `session-stop-all`, `session-restart`) that gracefully shut down daemon processes. However, there are cases where daemon processes become unresponsive or turn into zombies that don't respond to graceful shutdown signals. Users need a way to forcefully kill these stale processes.

## What You Need to Do

### 1. Implement the kill-all command

Add the `kill-all` command to the terminal command system:

- **Register the command** in `packages/playwright/src/mcp/terminal/commands.ts`:
  - Name: `kill-all`
  - Description: Something about forcefully killing daemon processes for stale/zombie cases
  - Category: `session`
  - This is a CLI-only command (no MCP tool equivalent)

- **Implement the handler** in `packages/playwright/src/mcp/terminal/program.ts`:
  - Create a `killAllDaemons()` function that:
    - Detects the platform (Windows vs Unix)
    - On Windows: Uses PowerShell to find and kill processes matching `run-mcp-server` and `--daemon-session`
    - On Unix/macOS: Uses `ps aux` to find and `SIGKILL` processes matching those patterns
    - Reports how many processes were killed (or "No daemon processes found" if none)
  - Add routing in both `handleSessionCommand()` and `program()` to handle the `kill-all` command
  - You'll need to import `execSync` from `child_process` alongside the existing `spawn` import

### 2. Update the skill documentation

The `.claude/skills/playwright-mcp-dev/SKILL.md` file contains instructions about updating documentation when adding CLI commands. Make sure to follow those conventions:

- **Update** `packages/playwright/src/skill/SKILL.md` to document the new command in the Sessions section (follow the format of existing commands)
- **Update** `packages/playwright/src/skill/references/session-management.md` to document when and how to use `kill-all` (in the Session Commands section and any relevant troubleshooting sections)

The documentation should explain what the command does (forceful termination of daemon processes) and when to use it (for stale/zombie processes that don't respond to normal session-stop commands).

## Files to Modify

- `packages/playwright/src/mcp/terminal/commands.ts` - Register the kill-all command
- `packages/playwright/src/mcp/terminal/program.ts` - Implement the killAllDaemons function and routing
- `packages/playwright/src/skill/SKILL.md` - Document the new command
- `packages/playwright/src/skill/references/session-management.md` - Document usage patterns

## Key Points

- The command should be in the `session` category like other session management commands
- The implementation needs to work on both Windows (PowerShell) and Unix (ps/kill)
- Match processes that contain both `run-mcp-server` and `--daemon-session` in their command line
- Documentation updates are required - look at how existing session commands are documented
