# Fix terminal e2e test flakiness with a proper terminal driver

## Problem

The terminal e2e tests in `packages/app/e2e/terminal/` are flaky. Tests check that a terminal element is visible or that a textarea child exists, but those DOM signals don't guarantee the terminal has actually connected and finished rendering its output. Because the terminal is canvas-backed and its write pipeline completes asynchronously, tests can type, switch tabs, or assert persistence before the rendered terminal state has caught up. This causes intermittent failures where tests appear to show input or persistence is broken when the terminal pipeline is simply still in flight.

## Expected Behavior

Terminal e2e tests should wait for the right signals — actual terminal output readiness — instead of just element visibility. This requires:

1. A test-only probe system that exposes terminal state (connected, rendered output, settled write count) via `window` for e2e access
2. Integration of the probe into the terminal component (`terminal.tsx`) so it tracks lifecycle events: init, connect, each data write, and settle
3. New e2e action helpers in `actions.ts` that wait for a terminal to be ready (`waitTerminalReady`) and type a command then wait for specific output (`runTerminal`)
4. The fixture setup must seed the probe's window state so the probe is active during tests

After implementing the code changes, update the project's e2e testing guide (`packages/app/e2e/AGENTS.md`) to document the new helpers and add a terminal testing section explaining the pattern for future test authors.

## Files to Look At

- `packages/app/src/components/terminal.tsx` — the terminal component that needs probe integration
- `packages/app/src/testing/terminal.ts` — should contain the new probe module (does not exist yet)
- `packages/app/e2e/actions.ts` — reusable action helpers where `waitTerminalReady` and `runTerminal` should live
- `packages/app/e2e/fixtures.ts` — test fixtures that need to seed the probe window state
- `packages/app/e2e/AGENTS.md` — e2e testing guide that should document the new helpers and terminal testing pattern
