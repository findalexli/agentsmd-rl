# Add kill-all helper for stale daemon processes

## Problem

The playwright-cli manages browser sessions using daemon processes. When daemon processes become stale or zombie processes (e.g., after crashes or unclean shutdowns), there is no way to forcefully terminate them. The existing `session-stop-all` command gracefully stops sessions, but it cannot handle processes that are no longer responding to normal shutdown signals.

## Expected Behavior

Add a `kill-all` CLI command that forcefully kills all daemon processes by scanning for processes matching the daemon pattern. This should work on both Unix (using `ps aux` + `SIGKILL`) and Windows (using PowerShell).

The command should:
- Find processes whose command line contains both `run-mcp-server` and `--daemon-session`
- Forcefully terminate matched processes
- Report how many processes were killed (or that none were found)

Additionally, the project's skill documentation and session management reference should be updated to document this new command, including guidance on when to use it (stale/zombie processes, unresponsive sessions).

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations and registration
- `packages/playwright/src/mcp/terminal/program.ts` — CLI command routing and handler logic
- `packages/playwright/src/skill/SKILL.md` — CLI skill documentation (Sessions section)
- `packages/playwright/src/skill/references/session-management.md` — Detailed session management reference
