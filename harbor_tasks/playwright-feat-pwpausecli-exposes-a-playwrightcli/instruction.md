# Add PWPAUSE=cli mode to expose a playwright-cli session during test runs

## Problem

When debugging a failing Playwright test, developers currently set `PWPAUSE=1` which pauses the test and opens an interactive inspector. However, AI agents and CLI-based workflows cannot debug test failures because there's no way to pause a test and interact with the page via the `playwright-cli` command-line tool. The system needs a programmatic way to connect to a paused test's browser context.

## Required Changes

### 1. PWPAUSE=cli handling in program.ts

In `packages/playwright/src/program.ts`, update the PWPAUSE environment variable handling:
- When `process.env.PWPAUSE === "cli"`, set `overrides.timeout = 0` (infinite test timeout) and `actionTimeout = 5000` (5 second action timeout)
- When `process.env.PWPAUSE` is truthy but NOT equal to `"cli"` (use an `else if`), set the existing pause behavior (`pause: true`, `headless: false`)
- `PWPAUSE=cli` should NOT trigger the old pause mode (no `pause: true`, no forced `headless: false`)

### 2. Test finish callbacks in testInfo.ts

In `packages/playwright/src/worker/testInfo.ts`, modify the callback mechanism that fires when a test function finishes:
- The property storing these callbacks must be named `_onDidFinishTestFunctionCallbacks` (plural)
- It must be initialized as a `Set` (e.g., `new Set<...>()`)
- Callbacks must be invoked using a `for...of` loop iterating over `this._onDidFinishTestFunctionCallbacks`
- This supports multiple handlers so both the artifacts recorder and the new daemon launcher can be notified

### 3. Daemon server in daemon.ts

In `packages/playwright/src/cli/daemon/daemon.ts`:
- The `startMcpDaemonServer` function must accept a `noShutdown` parameter
- When `noShutdown` is true, the daemon must remain running (guard browser close behind `if (!noShutdown)`)
- The daemon must import and use `decorateServer` from `packages/playwright-core/src/server/utils/network.ts`

### 4. Browser backend in browserBackend.ts

In `packages/playwright/src/mcp/test/browserBackend.ts`:
- Export an async function named `runDaemonForContext`
- This function must check `process.env.PWPAUSE` to determine if it should activate
- It must call `startMcpDaemonServer` from `packages/playwright/src/cli/daemon/daemon.ts`

### 5. Export decorateServer from network.ts

In `packages/playwright-core/src/server/utils/network.ts`:
- Export the `decorateServer` function so it can be imported by `daemon.ts`

### 6. Export sessionConfigFromArgs from program.ts

In `packages/playwright/src/cli/client/program.ts`:
- Export the `sessionConfigFromArgs` function so it can be used by other packages

### 7. SKILL.md update

Update `packages/playwright/src/skill/SKILL.md`:
- The description field should mention working with Playwright tests (not just browser automation)
- The `allowed-tools` in the frontmatter must include `Bash(npx:*)` and `Bash(npm:*)`
- The "Specific tasks" section should link to `references/playwright-tests.md`

### 8. New reference document

Create `packages/playwright/src/skill/references/playwright-tests.md` documenting:
- The `PWPAUSE=cli` environment variable for enabling CLI debugging mode
- The `playwright-cli` tool for connecting to paused test sessions
- The `--session=<name>` flag for specifying which session to connect to
- The workflow: set `PWPAUSE=cli`, run the test, wait for debugging instructions, then connect with `playwright-cli --session=<name>`