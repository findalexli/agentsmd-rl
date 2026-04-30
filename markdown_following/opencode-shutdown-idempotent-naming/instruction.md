# fix(process): prevent orphaned opencode subprocesses on shutdown

## Problem

The TUI thread shutdown logic has several issues that can lead to orphaned subprocesses:

1. **No idempotent shutdown**: Multiple shutdown paths (e.g., the `onExit` callback and a `finally` block) can trigger cleanup more than once, causing double-execution, hangs, or errors. There is no guard to ensure cleanup runs exactly once.

2. **Process listeners leak**: Event listeners for `uncaughtException`, `unhandledRejection`, and `SIGUSR2` are registered during startup but never removed during shutdown, preventing clean process exit.

3. **Worker termination not guaranteed**: If the worker's shutdown RPC call hangs, there's no timeout or forced termination fallback. The codebase provides a `withTimeout` utility at `@/util/timeout` that can bound promises, and `worker.terminate()` should always be called after the shutdown attempt regardless of outcome.

4. **Inline IIFEs reduce readability**: Worker path resolution and piped input handling use inline `iife()` calls that should be extracted to standalone named async helper functions.

5. **Verbose variable names**: Several local variables use multi-word camelCase names (`baseCwd`, `workerPath`, `networkOpts`, `shouldStartServer`) that don't follow the project's single-word naming convention and should be shortened to single-word alternatives.

## Expected Changes

### Shutdown Fix (TUI Thread)

- Make the shutdown function idempotent with a boolean guard that prevents re-entry
- During shutdown, unregister all three process event listeners using `process.off()`
- Bound the worker shutdown RPC with `withTimeout` from `@/util/timeout`
- Always call `worker.terminate()` after the shutdown attempt to guarantee cleanup
- Wrap the `tui()` call in `try/finally` so shutdown runs even on errors
- Extract a reusable error handler function for `uncaughtException`/`unhandledRejection` (replace inline arrows)

### Code Cleanup (TUI Thread)

- Extract the inline `iife()` calls to standalone named async functions
- Remove the `iife` utility import since it's no longer needed
- Replace the four verbose variable names with shorter single-word alternatives per the project's naming conventions

### Worker Simplification

- Remove the `Promise.race` with `setTimeout` timeout from the worker's `shutdown()` RPC handler — timeout handling is now the caller's responsibility
- The handler should directly `await Instance.disposeAll()`

### Agent Guidelines Update (AGENTS.md)

Add a naming enforcement subsection to the existing style guide that:
- Is clearly marked as mandatory for agent-written code
- Establishes single-word names as the default for new locals, params, and helpers
- Clarifies when multi-word names are acceptable
- Discourages new camelCase compounds when a short alternative exists
- Reminds to review and shorten identifiers before finishing edits
- Provides examples of good short names and verbose names to avoid

## Files to Look At

- The TUI thread implementation that manages the worker lifecycle
- The worker's RPC handler definitions
- AGENTS.md (project-level coding guidelines)

## Notes

- The codebase provides a `withTimeout` utility at `@/util/timeout` for bounding promises
- The project prefers single-word variable names as documented in AGENTS.md
- Use `.unref?.()` on `setTimeout` calls that shouldn't block process exit

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
