# Fix terminal e2e flakiness with a real terminal driver

## Problem

Terminal E2E tests are flaky because they wait on the wrong signals. A visible terminal, a mounted textarea, or an open WebSocket does not guarantee that terminal output has actually been rendered and settled. Because the terminal is canvas-backed and its write pipeline completes asynchronously, tests can type, switch tabs, or assert persistence before the rendered terminal state has caught up. This race makes tests intermittently look like input or persistence is broken when the terminal pipeline is still in flight.

## Expected Behavior

1. Create a dedicated terminal testing driver/probe that exposes terminal state (connected, rendered output, settled status) via a global `window.__opencode_e2e` object.
2. Add `waitTerminalReady()` and `runTerminal()` helpers in `packages/app/e2e/actions.ts` that use this driver to wait for actual terminal readiness and rendered output.
3. Integrate the probe into `packages/app/src/components/terminal.tsx` so it tracks connection state and write settlement.
4. Enable the test-only terminal driver in `packages/app/e2e/fixtures.ts` during test initialization.
5. **Documentation update**: Update `packages/app/e2e/AGENTS.md` to document the terminal testing pattern — specifically:
   - Terminal tests should type through the browser (not write to the PTY through the SDK)
   - Use `waitTerminalReady()` and `runTerminal()` helpers
   - These helpers use the fixture-enabled test-only terminal driver and wait for output after the terminal writer settles
   - Avoid `waitForTimeout` and custom DOM or `data-*` readiness checks

## Files to Look At

- `packages/app/src/testing/` — Create a new `terminal.ts` file here for the probe/driver
- `packages/app/e2e/actions.ts` — Add `waitTerminalReady()` and `runTerminal()` helpers here
- `packages/app/e2e/fixtures.ts` — Enable the terminal driver in the init script
- `packages/app/src/components/terminal.tsx` — Integrate the probe into the Terminal component
- `packages/app/e2e/AGENTS.md` — Document the terminal testing pattern

## Key Implementation Notes

The terminal probe should:
- Export `terminalAttr = "data-pty-id"` attribute name
- Track state: `connected`, `rendered` (accumulated output), `settled` (write count)
- Provide methods: `init()`, `connect()`, `render(data)`, `settle()`, `drop()`
- Only activate when `window.__opencode_e2e?.terminal?.enabled` is true

The helpers should:
- `waitTerminalReady()` — wait for terminal to be visible, have textarea, and be connected+settled
- `runTerminal()` — type a command via browser keyboard and wait for expected output token
