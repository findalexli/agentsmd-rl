# fix(process): prevent orphaned opencode subprocesses on shutdown

## Problem

The TUI thread shutdown logic has several issues that can lead to orphaned subprocesses:

1. **No idempotent shutdown**: Multiple shutdown paths could race or hang because there's no way to prevent double-execution.
2. **Process listeners leak**: Event listeners for uncaughtException, unhandledRejection, and SIGUSR2 are registered but never cleaned up during shutdown.
3. **Worker termination not guaranteed**: The worker's shutdown RPC call can hang indefinitely with no timeout or forced termination fallback.
4. **Complex inline IIFEs**: Worker path resolution and input handling use inline IIFEs that are hard to read and maintain.
5. **Verbose variable names**: Some variable names are longer than the codebase convention.

## Expected Changes

### Code Changes (packages/opencode/src/cli/cmd/tui/thread.ts)

1. **Add idempotent stop() function**:
   - Prevent the stop function from running cleanup logic more than once
   - Unregister all process event listeners that were registered during startup
   - Call worker.shutdown() with bounded timeout
   - Always call worker.terminate() to force worker cleanup

2. **Extract helper functions**:
   - A function to resolve the worker path
   - A function to handle piped stdin + prompt

3. **Simplify variable names per existing AGENTS.md style** — use shorter single-word names

4. **Add withTimeout import** from @/util/timeout, remove unused iife import

5. **Use try/finally** to ensure stop() is called even if tui() throws

### Code Changes (packages/opencode/src/cli/cmd/tui/worker.ts)

Simplify shutdown() RPC handler — the timeout logic should now be the caller's responsibility.

### Config Changes (AGENTS.md)

Add a new **mandatory** "Naming Enforcement (Read This)" subsection under the existing "### Naming" section with rules for short variable names.

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/thread.ts` — Main TUI thread with worker lifecycle management
- `packages/opencode/src/cli/cmd/tui/worker.ts` — Worker thread RPC handlers
- `AGENTS.md` — Agent coding guidelines (must add Naming Enforcement section)

## Notes

- The Bun runtime provides withTimeout utility at @/util/timeout
- The codebase prefers single-word variable names per AGENTS.md
- Always use .unref?.() on setTimeout calls that shouldn't block process exit