Add a `kill-all` CLI command to the playwright-cli tool that forcefully terminates all daemon processes. This is needed for handling stale or zombie MCP server processes that may remain after crashes or unexpected shutdowns.

The implementation should:
1. Add a new CLI command in the `session` category with:
   - Command name: `kill-all`
   - Description: `Forcefully kill all daemon processes` (use this exact phrase)
   - Variable name: `killAll`
2. Implement a function that:
   - Detects running daemon processes by looking for processes containing `run-mcp-server` and `--daemon-session` in their command line
   - Handles both Windows (using PowerShell) and Unix (using `ps` + SIGKILL) platforms
   - Reports how many processes were killed
   - Gracefully handles cases where no processes are found
3. Register the command in `commands.ts` and `program.ts` at these paths:
   - `packages/playwright/src/mcp/terminal/commands.ts`
   - `packages/playwright/src/mcp/terminal/program.ts`

**Important:** After implementing the code changes, you must update the skill documentation to reflect this new command. The project maintains documentation in:
- `packages/playwright/src/skill/SKILL.md` - Main skill file with all CLI commands
- `packages/playwright/src/skill/references/session-management.md` - Detailed session management guide

The SKILL.md should list `kill-all` in the Sessions section following the same format as other session commands (e.g., `playwright-cli session-list`). Include the comment `# forcefully kill all daemon processes (for stale/zombie processes)` after the command.

The session-management.md should document when to use this command (for zombie/stale/unresponsive processes) using the phrase `playwright-cli kill-all`.

Refer to `.claude/skills/playwright-mcp-dev/SKILL.md` for guidance on the CLI command development workflow and documentation requirements.
