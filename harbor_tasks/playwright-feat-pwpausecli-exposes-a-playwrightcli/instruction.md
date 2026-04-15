# Add PWPAUSE=cli mode to expose a playwright-cli session during test runs

## Problem

When debugging a failing Playwright test, developers currently have to set `PWPAUSE=1` which pauses the test and opens an interactive inspector. However, there's no way to pause a test and interact with the page via the `playwright-cli` command-line tool. This means AI agents and CLI-based workflows can't easily debug test failures — they need a programmatic way to connect to a paused test's browser context.

## What Needs to Change

When the environment variable `PWPAUSE` is set to the string `cli`, the test runner should:

1. **Not treat it as the old pause mode** — the existing `PWPAUSE` (truthy) behavior should still work for non-`cli` values, but `PWPAUSE=cli` should NOT set `pause: true` or force `headless: false`.
2. **Set appropriate timeouts** — `PWPAUSE=cli` should set the test timeout to 0 (infinite) and a short action timeout so the test pauses on failure but individual actions fail quickly.
3. **Start a daemon server after the test finishes** — After the test function finishes (on error or completion), expose the browser context as a `playwright-cli` daemon session so the CLI can connect to it and inspect the page. The daemon should remain running until the test run is explicitly stopped.
4. **Support multiple finish handlers** — The current callback mechanism for when a test finishes only supports a single handler. It needs to support multiple handlers so that both the artifacts recorder and the new daemon launcher can be notified.
5. **Expose internal utilities** — Some internal functions used by the daemon server and CLI client configuration need to be made accessible from other packages.

## Agent Config Update

After implementing the code changes, update the project's skill documentation to reflect the new capability:

- The `packages/playwright/src/skill/SKILL.md` should be updated: the description should mention working with Playwright tests (not just browser automation), and the `allowed-tools` should include `Bash(npx:*)` and `Bash(npm:*)` since agents now need to run test commands.
- A new reference document should be added at `packages/playwright/src/skill/references/playwright-tests.md` explaining how to run and debug Playwright tests using `PWPAUSE=cli`. It should cover the workflow: set the env var, run the test, wait for the debugging instructions, then use `playwright-cli --session=<name>` to connect.
- The SKILL.md "Specific tasks" section should link to this new reference.