# Add PWPAUSE=cli mode to expose a playwright-cli session during test runs

## Problem

When debugging a failing Playwright test, developers currently set `PWPAUSE=1` which pauses the test and opens an interactive inspector. However, AI agents and CLI-based workflows cannot debug test failures because there's no way to pause a test and interact with the page via the `playwright-cli` command-line tool. The system needs a programmatic way to connect to a paused test's browser context.

## Required Behavior

### 1. PWPAUSE=cli handling in program.ts

In `packages/playwright/src/program.ts`, the PWPAUSE environment variable handling must distinguish between two modes:
- When `process.env.PWPAUSE` equals `"cli"`, the test should run with the test timeout disabled and a short action timeout to keep actions responsive during debugging
- When `process.env.PWPAUSE` is set to any other truthy value (not `"cli"`), it should retain the existing pause behavior (pause mode, headless disabled)
- The `"cli"` mode must not trigger the old pause behavior (no pause flag, no forced headless false)

### 2. Test finish callbacks in testInfo.ts

In `packages/playwright/src/worker/testInfo.ts`, the mechanism for callbacks when a test function finishes must support multiple handlers:
- Multiple callbacks should be able to register and all be invoked when the test function completes
- This supports both the artifacts recorder and the new daemon launcher being notified when a test function completes

### 3. Daemon server in daemon.ts

In `packages/playwright/src/cli/daemon/daemon.ts`:
- `startMcpDaemonServer` must accept an additional parameter that prevents automatic shutdown
- When this parameter indicates the daemon should stay alive, the daemon must remain running and must not close the browser when the browser context closes
- The daemon must import and use `decorateServer` from `packages/playwright-core/src/server/utils/network.ts`

### 4. Browser backend in browserBackend.ts

In `packages/playwright/src/mcp/test/browserBackend.ts`:
- Export an async function `runDaemonForContext` that launches the MCP daemon for a test context
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

## Code Style Requirements

This project uses ESLint for code quality. After making your changes, ensure they pass the repository's lint checks. TypeScript types must also be correct — run `npm run tsc` to type-check.
