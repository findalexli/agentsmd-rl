# Add kill-all command for daemon process cleanup

## Problem

The playwright-cli MCP server can leave behind stale or zombie daemon processes when sessions don't shut down cleanly. Users need a way to forcefully terminate all daemon processes.

## Task

Add a `kill-all` command that:
1. Finds all running daemon processes (matching `run-mcp-server` and `--daemon-session`)
2. Forcefully terminates them with SIGKILL (Unix) or Stop-Process (Windows)
3. Reports how many processes were killed

## Files to modify

1. **packages/playwright/src/mcp/terminal/commands.ts**: Add the `kill-all` command declaration to the commands array
2. **packages/playwright/src/mcp/terminal/program.ts**: Implement the daemon killing logic

## Implementation notes

The command should:
- Import `execSync` from `child_process` for cross-platform process enumeration
- Use `ps aux` on Unix/Linux/macOS to find daemon processes by command line pattern
- Use PowerShell `Get-CimInstance` on Windows to find and kill processes
- Use `process.kill(pid, 'SIGKILL')` on Unix for forceful termination
- Handle errors silently (no processes to kill is a valid state)
- Output the count of killed processes in the format: "Killed N daemon process(es)" or "No daemon processes found."

## Documentation update

After implementing the command, update the documentation to reflect the new capability:
- Update `packages/playwright/src/skill/SKILL.md` to include `kill-all` in the Sessions section
- Update `packages/playwright/src/skill/references/session-management.md` to document when and how to use `kill-all` for zombie processes

The documentation should clearly indicate this command is for forcefully killing stale/zombie processes when normal session cleanup fails.
