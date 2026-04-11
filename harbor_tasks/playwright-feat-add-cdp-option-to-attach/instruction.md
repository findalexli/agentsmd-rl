# Add --cdp option to playwright-cli attach command

## Problem

The `playwright-cli attach` command currently only supports attaching to a browser by name/endpoint via a positional argument. There is no way to connect to an existing browser (such as an Electron app launched with `--remote-debugging-port`) via its Chrome DevTools Protocol (CDP) endpoint URL.

Additionally, the `--extension` option for connecting to a browser extension is currently on the `open` command, but logically belongs on `attach` since it connects to an already-running browser rather than launching a new one.

## Expected Behavior

1. The `attach` command should accept a `--cdp <url>` option to connect to an existing browser via its CDP endpoint
2. The `--extension` option should be moved from `open` to `attach`, with support for specifying a browser name (e.g., `--extension=chrome`)
3. The attach command should also accept an `--endpoint` named option as an alternative to the positional argument
4. Conflicting usage (positional target + named options like `--cdp`) should produce an error

## Files to Look At

- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI argument parsing, type definitions for command options
- `packages/playwright-core/src/tools/cli-daemon/commands.ts` — CLI command declarations with zod schemas
- `packages/playwright-core/src/tools/cli-daemon/program.ts` — daemon CLI flag registration
- `packages/playwright-core/src/tools/mcp/config.ts` — config resolution, must handle cdpEndpoint
- `packages/playwright-core/src/tools/cli-client/session.ts` — passes flags from client to daemon
- `packages/playwright-core/src/tools/cli-client/registry.ts` — session name resolution (simplify if needed)
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI usage documentation. The `--extension` docs must be moved from the "Open parameters" section to an appropriate section for the `attach` command.
