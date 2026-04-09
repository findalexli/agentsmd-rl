# opencode: prevent orphaned subprocesses on shutdown

## Problem

The TUI thread's shutdown is fragile — if the worker process becomes unhealthy during exit, the process can hang indefinitely. The shutdown path doesn't guard against double-invocation, doesn't always terminate the worker, and doesn't unregister process event listeners. Additionally, child processes can outlive the parent when MCP client teardown hangs.

The worker's `shutdown()` function wraps `Instance.disposeAll()` in a `Promise.race` with a setTimeout, but this timeout is handled at the wrong layer.

## Expected Behavior

1. The TUI thread shutdown must be **idempotent** — calling it twice must be safe. It must always terminate the worker and unregister process listeners (`uncaughtException`, `unhandledRejection`, `SIGUSR2`).
2. The worker shutdown call must be **timeout-bounded** using the existing `withTimeout` utility, so a hung worker cannot block process exit.
3. The code must use a `try/finally` around the TUI invocation to guarantee cleanup runs.
4. The inline logic for resolving the worker path and building the prompt string should be extracted into standalone helper functions (`target` and `input`) for clarity.

After fixing the code, update `AGENTS.md` to add a **Naming Enforcement** section that makes the existing single-word naming preference mandatory. The section should:
- Declare it as a mandatory rule for agent-written code
- List preferred short names (e.g., `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`)
- List multi-word examples to avoid (e.g., `inputPID`, `existingClient`, `connectTimeout`, `workerPath`)
- Place it immediately after the existing "Naming" section

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/thread.ts` — TUI thread command with worker lifecycle and shutdown
- `packages/opencode/src/cli/cmd/tui/worker.ts` — worker's shutdown function
- `AGENTS.md` — agent instructions with style guide and naming conventions
