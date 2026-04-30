# opencode: prevent orphaned subprocesses on shutdown

## Problem

The TUI thread's shutdown is fragile — if the worker process becomes unhealthy during exit, the process can hang indefinitely. The shutdown path doesn't guard against double-invocation, doesn't always terminate the worker, and doesn't unregister process event listeners. Additionally, child processes can outlive the parent when MCP client teardown hangs.

The worker's `shutdown()` function wraps `Instance.disposeAll()` in a `Promise.race` with a setTimeout, but the timeout handling is layered incorrectly.

## Expected Behavior

1. The TUI thread shutdown must be **idempotent** — calling it twice must be safe. It must always terminate the worker and unregister process listeners (`uncaughtException`, `unhandledRejection`, `SIGUSR2`).
2. The worker shutdown call must be **timeout-bounded** using the existing `withTimeout` utility, so a hung worker cannot block process exit.
3. The code must use a `try/finally` around the TUI invocation to guarantee cleanup runs.
4. The inline logic for resolving the worker path and building the prompt string should be extracted into standalone helper functions.

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/thread.ts` — TUI thread command with worker lifecycle and shutdown
- `packages/opencode/src/cli/cmd/tui/worker.ts` — worker's shutdown function
- `AGENTS.md` — agent instructions with style guide and naming conventions

## AGENTS.md Naming Requirements

After fixing the code, update `AGENTS.md` to add a **Naming Enforcement** section immediately after the existing "Naming" section. The section must:

- Declare single-word naming as a **mandatory** rule for agent-written code
- List preferred short names as examples (e.g., `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`)
- List multi-word examples to avoid (e.g., `inputPID`, `existingClient`, `connectTimeout`, `workerPath`)

The section header must contain the phrase "Naming Enforcement" and the mandatory rule text must contain the exact string "THIS RULE IS MANDATORY".

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
