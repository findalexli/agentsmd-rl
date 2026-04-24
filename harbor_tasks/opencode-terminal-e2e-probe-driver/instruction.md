# Fix terminal e2e test flakiness with a proper terminal driver

## Problem

The terminal e2e tests in `packages/app/e2e/terminal/` are flaky. Tests check that a terminal element is visible or that a textarea child exists, but those DOM signals don't guarantee the terminal has actually connected and finished rendering its output. Because the terminal is canvas-backed and its write pipeline completes asynchronously, tests can type, switch tabs, or assert persistence before the rendered terminal state has caught up. This causes intermittent failures where tests appear to show input or persistence is broken when the terminal pipeline is simply still in flight.

## Expected Behavior

Terminal e2e tests must wait for actual terminal output readiness — not just DOM visibility. To enable this:

1. **Create a test-only probe module** at `packages/app/src/testing/terminal.ts` that exposes terminal state for e2e access via `window`. The probe must track per-terminal state with these fields:
   - `connected: boolean` — whether the WebSocket has opened
   - `rendered: string` — concatenated output received so far
   - `settled: number` — count of write completions (incremented each time a write batch finishes)

   Store the state under `window.__opencode_e2e.terminal.terminals[id]`. The window state structure should be `{ enabled: true, terminals: {} }`. The probe module must export a `terminalAttr` constant set to the string `"data-pty-id"`. The probe must also have a method to remove/clean up a terminal entry when a terminal is disposed.

2. **Integrate the probe into the terminal component** (`packages/app/src/components/terminal.tsx`) so it tracks lifecycle events:
   - Initialize tracking when the terminal mounts
   - Mark as connected when the WebSocket opens
   - Record rendered data and increment settled count for each batch of output written to the PTY
   - Clean up when the terminal unmounts or is disposed
   - The terminal's root element must have the `data-pty-id` attribute set to the PTY ID

3. **Add new e2e action helpers** in `packages/app/e2e/actions.ts` named `waitTerminalReady` and `runTerminal` that wait for a terminal to reach the "ready" state (connected and having completed at least one write) before proceeding. These helpers should use `terminalSelector` from `selectors.ts` to locate terminal elements.

4. **Set up the test harness** in `packages/app/e2e/fixtures.ts` so the `window.__opencode_e2e.terminal` tree is available during tests via `page.addInitScript`.

5. **Update `packages/app/e2e/AGENTS.md`** to document `waitTerminalReady` and `runTerminal` helpers and add a "Terminal Tests" section explaining the pattern: type through the browser, use the helpers instead of `waitForTimeout` or custom DOM checks.

## Files to Look At

- `packages/app/src/components/terminal.tsx` — the terminal component that needs probe integration
- `packages/app/src/testing/terminal.ts` — the new probe module (does not exist yet)
- `packages/app/e2e/actions.ts` — where `waitTerminalReady` and `runTerminal` should be added
- `packages/app/e2e/fixtures.ts` — where the init script seeding goes
- `packages/app/e2e/selectors.ts` — contains `terminalSelector`
- `packages/app/e2e/AGENTS.md` — e2e testing guide to update

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
