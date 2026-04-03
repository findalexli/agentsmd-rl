# Add --cdp option to playwright-cli attach command

## Problem

The `playwright-cli attach` command currently only supports attaching to browsers by a named target (a bound browser name). There's no way to connect to an existing browser instance (including Electron apps) that exposes a Chrome DevTools Protocol (CDP) endpoint URL. Users who launch a browser with `--remote-debugging-port` cannot use `playwright-cli` to interact with it.

Additionally, the `--extension` flag is currently on the `open` command, but it conceptually belongs on `attach` since connecting via browser extension is an attach operation, not an open operation.

## Expected Behavior

1. `playwright-cli attach --cdp=<url>` should connect to a browser via its CDP endpoint URL
2. `playwright-cli attach --extension` should connect via browser extension (moved from `open`)
3. The `attach` command's positional target name argument should become optional (since `--cdp`, `--endpoint`, and `--extension` provide alternative attach methods)
4. Using a positional target name together with `--cdp`, `--endpoint`, or `--extension` should produce a clear error
5. The `--cdp` option must be threaded through the session, daemon, and config layers

## Files to Look At

- `packages/playwright-core/src/tools/cli-daemon/commands.ts` — command declarations with Zod schemas for `open` and `attach`
- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI argument parsing and the `attach` case handler
- `packages/playwright-core/src/tools/cli-client/session.ts` — session arg forwarding to daemon
- `packages/playwright-core/src/tools/cli-daemon/program.ts` — daemon-side option registration
- `packages/playwright-core/src/tools/mcp/config.ts` — config resolution (must pass CDP endpoint and update isolated browser check)

After implementing the code changes, update the relevant skill documentation to reflect the new command structure. The `--extension` example should be moved from `open` to `attach`, and the documentation should accurately represent which options belong to which command.
