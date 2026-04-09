# fix(process): prevent orphaned opencode subprocesses on shutdown

## Problem

The opencode TUI and MCP client cleanup had several issues that could leave subprocesses orphaned:

1. **TUI thread shutdown was not idempotent** - Multiple exit paths could race, leaving workers and event listeners in an inconsistent state
2. **Worker shutdown used `Promise.race` with timeout** - This could interrupt `Instance.disposeAll()` mid-cleanup, leaving sessions in an inconsistent state
3. **MCP client cleanup only signaled direct children** - MCP servers like `chrome-devtools-mcp` spawn grandchild processes (e.g., Chrome browser) that the SDK never reaches, leaving them orphaned
4. **Timer kept process alive** - The `setTimeout` for `checkUpgrade` could keep the process alive unnecessarily
5. **Missing naming guidelines in AGENTS.md** - No enforcement rules for agent-written code naming conventions

## Expected Behavior

1. TUI thread shutdown should be idempotent with a `stop()` function that:
   - Unregisters all process event listeners (`uncaughtException`, `unhandledRejection`, `SIGUSR2`)
   - Uses timeout-bounded shutdown with `withTimeout`
   - Always calls `worker.terminate()`

2. Worker shutdown should use full `await Instance.disposeAll()` instead of racing with a timeout

3. MCP cleanup should kill the full descendant process tree before closing clients:
   - Add `descendants()` function using `pgrep -P` to find child PIDs recursively
   - Send `SIGTERM` to all descendants before calling `client.close()`

4. setTimeout for `checkUpgrade` should use `.unref?.()` to prevent keeping the process alive

5. AGENTS.md should have a mandatory "Naming Enforcement" section documenting single-word naming rules

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/thread.ts` - TUI thread shutdown logic
- `packages/opencode/src/cli/cmd/tui/worker.ts` - Worker shutdown logic
- `packages/opencode/src/mcp/index.ts` - MCP client cleanup
- `AGENTS.md` - Agent coding guidelines

## References

- PR #15924: fix(process): prevent orphaned opencode subprocesses on shutdown
- See AGENTS.md "Naming Enforcement" section for coding standards
