# Add kill-all command to Playwright MCP CLI

## Task Description

Implement a new `kill-all` command for the Playwright MCP CLI that forcefully terminates all running daemon processes. This is useful for cleaning up stale or zombie processes that may remain after sessions become unresponsive.

## Requirements

### Command Declaration (commands.ts)

A `kill-all` session command must be declared in `packages/playwright/src/mcp/terminal/commands.ts`:

- Command name: `'kill-all'`
- Description: must contain the phrase "Forcefully kill all daemon processes" (for stale/zombie processes)
- Category: `'session'`
- `toolName`: empty string (CLI-only, not an MCP tool)
- `toolParams`: returns empty object `() => ({})`
- The command must be added to the `commandsArray`

### Command Handler (program.ts)

The `kill-all` command must be handled in `packages/playwright/src/mcp/terminal/program.ts`:
- Import `execSync` from `'child_process'` (alongside any existing imports from that module)
- Define an async function that terminates all daemon processes, with return type `Promise<void>`
- The top-level command dispatch must handle the `'kill-all'` command
- The session command handler must also handle `'kill-all'` by calling the daemon termination function

### Daemon Termination Implementation

The daemon termination function must:
- Detect the platform using `os.platform()`
- On Windows (`win32`): Use PowerShell to find and kill processes matching `run-mcp-server` with `--daemon-session` flag
- On Unix: Use process listing to find daemon processes matching `run-mcp-server` and `--daemon-session`, extract PIDs, and send SIGKILL
- Report the number of processes killed (or "No daemon processes found" if none)
- Handle errors silently (no processes to kill is not an error)

### Documentation (SKILL.md and session-management.md)

Document the `kill-all` command:
- In `packages/playwright/src/skill/SKILL.md`: Add the command to the Sessions section with a comment explaining it's for forcefully killing daemon processes (stale/zombie processes)
- In `packages/playwright/src/skill/references/session-management.md`: Add to the "Stop Sessions" section and include in the "Managing Multiple Sessions" example, explaining when to use it (unresponsive or zombie processes)

## Verification

After implementation:
- TypeScript should compile without errors in the terminal package
- All text assertions in the test suite should pass

## Notes

- The kill-all command is a "break glass" option for manual cleanup - it forcefully terminates processes without graceful shutdown
- This is for edge cases (stale/zombie processes), not normal session management