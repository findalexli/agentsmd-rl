Add a `kill-all` CLI command to the playwright-cli tool that forcefully terminates all daemon processes. This is needed for handling stale or zombie MCP server processes that may remain after crashes or unexpected shutdowns.

The implementation should:
1. Add a new CLI command in the `session` category with:
   - Command name: `kill-all`
   - Description: `Forcefully kill all daemon processes` (use this exact phrase)
   - Variable name: `killAll`
2. Implement a function that:
   - Detects running daemon processes by looking for processes containing `run-mcp-server` and `--daemon-session` in their command line
   - Handles both Windows (using PowerShell) and Unix (using `ps` + SIGKILL) platforms, checking for `win32` platform
   - Reports how many processes were killed
   - Gracefully handles cases where no processes are found
3. Register the command in the terminal CLI module files (look for where other session commands like `session-list` and `session-stop-all` are declared and registered).

**Important:** After implementing the code changes, you must update the skill documentation to reflect this new command. Update the main skill file (which documents all CLI commands in a "Sessions" section with a `playwright-cli session-list` example) and the session management reference guide (which explains when and how to use session commands).

The main skill file should list `kill-all` in the Sessions code block following the same format as other session commands (e.g., `playwright-cli session-list`). Include the comment `# forcefully kill all daemon processes (for stale/zombie processes)` after the command.

The session management reference should document when to use this command (for zombie/stale/unresponsive processes) using the phrase `playwright-cli kill-all`.

Refer to `.claude/skills/playwright-mcp-dev/SKILL.md` for guidance on the CLI command development workflow and documentation requirements.
