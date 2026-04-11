# Implement direct daemon startup and rename session flag

## Problem

The `playwright-cli` daemon startup is unreliable. Currently, after spawning the daemon child process, the parent polls for socket availability with retries and arbitrary delays. This creates race conditions — the parent may timeout before the daemon is ready, or waste time waiting even though the daemon has already failed (e.g., due to a missing browser executable). Additionally, if the browser fails to launch, the error information is lost or delayed since the daemon only communicates through the socket and log files.

The session flag is also named `-b` (for "browser") which is confusing since the concept is really a "session", not a browser.

## Expected Behavior

1. **Direct daemon startup**: Instead of polling for a socket, the parent process should read the daemon's stdout to know when it's ready (or if it failed). The daemon should:
   - Launch the browser context directly at startup (not lazily on first tool call)
   - Signal success or failure back to the parent via stdout markers
   - Exit cleanly if the browser context closes

2. **Rename session flag**: The `-b` alias should be renamed to `-s` everywhere — argument parsing, help text, error messages, and console output.

3. **Error message improvements**: When a browser isn't installed, the error message should include the specific browser channel/name rather than a generic message.

## Files to Look At

- `packages/playwright/src/mcp/terminal/daemon.ts` — daemon server startup logic
- `packages/playwright/src/mcp/terminal/program.ts` — CLI session management, argument parsing
- `packages/playwright/src/mcp/program.ts` — main MCP program entry, daemon startup path
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — CLI help text generation
- `packages/playwright/src/mcp/browser/browserContextFactory.ts` — browser launch error handling

After making the code changes, update the relevant skill documentation files to reflect the flag rename. The project's dev instructions specify that CLI command changes should be accompanied by documentation updates.
