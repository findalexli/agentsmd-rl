# Fix terminal e2e flakiness with a real terminal driver

## Problem

Terminal e2e tests are flaky because they rely on timing-based checks (`waitForTimeout`) and DOM visibility assertions that don't actually verify the terminal is ready to receive input. The terminal has internal state (connection, rendering) that needs to be stable before tests interact with it.

Specific issues:
1. Tests use `await expect(terminal).toBeVisible()` which doesn't wait for the terminal to be fully initialized
2. Tests type into the terminal before it's ready, causing race conditions
3. Tests use `waitForTimeout` instead of waiting for actual terminal state
4. No way to verify that terminal output has been rendered before assertions

## Expected Behavior

Implement a terminal testing driver that:
1. Tracks terminal connection state through a window-level probe
2. Accumulates rendered output for assertions
3. Provides explicit "settled" state when terminal is ready
4. Exports helper functions `waitTerminalReady()` and `runTerminal()` in `actions.ts`
5. Updates `AGENTS.md` documentation for terminal testing patterns

## Files to Look At

- `packages/app/e2e/actions.ts` — add `waitTerminalReady()` and `runTerminal()` helpers
- `packages/app/e2e/AGENTS.md` — document the terminal testing pattern
- `packages/app/e2e/fixtures.ts` — initialize terminal testing state in `seedStorage`
- `packages/app/src/components/terminal.tsx` — integrate terminal probe hooks
- `packages/app/src/testing/terminal.ts` — new testing utility (to create)

Key patterns from AGENTS.md:
- Type into terminals through the browser (via `page.keyboard`), not through the SDK/PTY
- Use `waitTerminalReady()` before interacting with terminals
- Use `runTerminal()` to type commands and wait for output
- Avoid `waitForTimeout` and custom DOM readiness checks
