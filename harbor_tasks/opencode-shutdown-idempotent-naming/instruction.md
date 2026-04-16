# fix(process): prevent orphaned opencode subprocesses on shutdown

## Problem

The TUI thread shutdown logic has several issues that can lead to orphaned subprocesses:

1. **No idempotent shutdown**: Multiple shutdown paths could race or hang because there's no way to prevent double-execution. The stop() function needs a guard to ensure cleanup logic runs exactly once.

2. **Process listeners leak**: Event listeners for `uncaughtException`, `unhandledRejection`, and `SIGUSR2` are registered during startup but never cleaned up during shutdown.

3. **Worker termination not guaranteed**: The worker's shutdown RPC call can hang indefinitely with no timeout or forced termination fallback.

4. **Complex inline IIFEs**: Worker path resolution and input handling use inline IIFEs that are hard to read and maintain. These should be standalone helper functions.

5. **Verbose variable names**: Some variable names are longer than the codebase convention. Specifically:
   - `baseCwd` should be renamed to `root`
   - `workerPath` should be renamed to `file`
   - `networkOpts` should be renamed to `network`
   - `shouldStartServer` should be renamed to `external`

## Expected Changes

### Code Changes (TUI thread)

Fix the shutdown logic in the main TUI thread file to ensure idempotent cleanup:

1. **Add idempotent stop() function** with these exact implementation details:
   - Use a variable named `stopped` initialized to `false` as a guard flag
   - At the start of stop(), check `if (stopped) return` to prevent double-execution
   - Set `stopped = true` before proceeding with cleanup
   - Unregister all three process event listeners using `process.off()` for `uncaughtException`, `unhandledRejection`, and `SIGUSR2`
   - Call worker.shutdown() with a bounded timeout (5000ms)
   - Always call `worker.terminate()` after shutdown attempt to force cleanup

2. **Extract helper functions** from the inline IIFEs:
   - Create an `async function target()` that resolves the worker path
   - Create an `async function input()` that handles piped stdin + prompt
   - Remove any `iife` imports since they are no longer needed

3. **Simplify variable names** per the list above — replace `baseCwd`, `workerPath`, `networkOpts`, and `shouldStartServer` with their shorter equivalents.

4. **Add timeout utility import** from `@/util/timeout` and use `withTimeout()` to wrap the shutdown call.

5. **Wrap tui() call in try/finally** to ensure stop() is called even if tui() throws.

6. **Extract a reusable error handler** as a named function (not inline arrow) and register it for both `uncaughtException` and `unhandledRejection`.

### Code Changes (Worker)

Simplify the worker shutdown() RPC handler — remove the Promise.race with timeout since the timeout logic is now the caller's responsibility. The worker should directly `await Instance.disposeAll()`.

### Config Changes (Agent Guidelines)

Add a new mandatory naming enforcement subsection under the existing Naming section in the agent coding guidelines file. The section must:
- Be titled "### Naming Enforcement (Read This)"
- Include the mandatory rule statement: "THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE"
- Include a bullet point stating: "Use single word names by default for new locals, params, and helper functions"
- Include a bullet point stating: "Multi-word names are allowed only when a single word would be unclear or ambiguous"
- Include a bullet point stating: "Do not introduce new camelCase compounds when a short single-word alternative is clear"
- Include a bullet point stating: "Before finishing edits, review touched lines and shorten newly introduced identifiers where possible"
- List good short names to prefer including: `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`
- List examples to avoid including: `inputPID`, `existingClient`, `connectTimeout`, `workerPath`

## Files to Look At

- The main TUI thread implementation file (contains worker lifecycle management)
- The worker thread RPC handlers file
- The agent coding guidelines file (contains naming conventions)

## Notes

- The Bun runtime provides withTimeout utility at @/util/timeout
- The codebase prefers single-word variable names as documented in the agent coding guidelines
- Always use .unref?.() on setTimeout calls that shouldn't block process exit
