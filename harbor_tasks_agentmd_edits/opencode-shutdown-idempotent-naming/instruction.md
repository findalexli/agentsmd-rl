# fix(process): prevent orphaned opencode subprocesses on shutdown

## Problem

The TUI thread shutdown logic has several issues that can lead to orphaned subprocesses:

1. **No idempotent shutdown**: There's no centralized `stop()` function with a `stopped` flag, so multiple shutdown paths could race or hang.
2. **Process listeners leak**: Event listeners for `uncaughtException`, `unhandledRejection`, and `SIGUSR2` are registered but never unregistered during cleanup.
3. **Worker termination not guaranteed**: The worker's `shutdown()` RPC call can hang indefinitely with no timeout or forced termination fallback.
4. **Complex inline IIFEs**: Worker path resolution and input handling use inline IIFEs that are hard to read and maintain.
5. **Verbose variable names**: Variable names like `baseCwd`, `workerPath`, `networkOpts`, `shouldStartServer` are longer than necessary.

## Expected Changes

### Code Changes (packages/opencode/src/cli/cmd/tui/thread.ts)

1. **Add idempotent `stop()` function**:
   - Use a `stopped` flag to prevent double-execution
   - Unregister all process event listeners
   - Call `worker.shutdown()` with a 5-second timeout using `withTimeout`
   - Always call `worker.terminate()` to force cleanup

2. **Extract helper functions**:
   - `target()`: Resolve worker path (replaces inline IIFE)
   - `input()`: Handle piped stdin + prompt (replaces inline IIFE)

3. **Simplify variable names** per existing AGENTS.md style:
   - `baseCwd` → `root`
   - `workerPath` → `file`
   - `networkOpts` → `network`
   - `shouldStartServer` → `external`

4. **Add withTimeout import** from `@/util/timeout`, remove unused `iife` import

5. **Use try/finally** to ensure `stop()` is called even if `tui()` throws

### Code Changes (packages/opencode/src/cli/cmd/tui/worker.ts)

Simplify `shutdown()` RPC handler - remove the `Promise.race` with 5-second timeout (this timeout is now the caller's responsibility in `thread.ts`).

### Config Changes (AGENTS.md)

Add a new **mandatory** "Naming Enforcement (Read This)" subsection under the existing "### Naming" section. This section should:

- Mark the rule as "THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE"
- Specify that single-word names are the default for locals, params, and helpers
- List good short names: `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`
- List examples to avoid: `inputPID`, `existingClient`, `connectTimeout`, `workerPath`
- Include a rule to review touched lines and shorten newly introduced identifiers before finishing

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/thread.ts` — Main TUI thread with worker lifecycle management
- `packages/opencode/src/cli/cmd/tui/worker.ts` — Worker thread RPC handlers
- `AGENTS.md` — Agent coding guidelines (must add Naming Enforcement section)

## Notes

- The Bun runtime provides `withTimeout` utility at `@/util/timeout`
- The codebase prefers single-word variable names per AGENTS.md
- Always use `.unref?.()` on `setTimeout` calls that shouldn't block process exit
