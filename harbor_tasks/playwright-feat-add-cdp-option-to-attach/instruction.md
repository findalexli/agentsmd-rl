# Add --cdp option to playwright-cli attach command

## Problem

The `playwright-cli attach` command currently only supports attaching to a browser by name/endpoint via a positional argument. There is no way to connect to an existing browser (such as an Electron app launched with `--remote-debugging-port`) via its Chrome DevTools Protocol (CDP) endpoint URL.

Additionally, the `--extension` option for connecting to a browser extension is currently on the `open` command, but logically belongs on `attach` since it connects to an already-running browser rather than launching a new one.

## Expected Behavior

1. The `attach` command should accept a `--cdp <url>` option to connect to an existing browser via its CDP endpoint URL.

2. The `--extension` option should be moved from `open` to `attach`, with support for specifying a browser name (e.g., `--extension=chrome`).

3. The attach command should also accept an `--endpoint` named option as an alternative to the positional argument for specifying the target browser endpoint.

4. Conflicting usage (providing both a positional target AND named options like `--cdp`, `--endpoint`, or `--extension`) should produce an error. The error should indicate that these options cannot be used together with a positional target.

5. The implementation must:
   - Add `cdp` to the global CLI argument parsing in the cli-client program
   - Add a `cdp` field to the attach command's options schema in the cli-daemon commands
   - Register a `--cdp` CLI flag in the cli-daemon program
   - Pass the `--cdp` flag value from cli-client to cli-daemon through the session management code
   - Map the CLI `cdp` option to `cdpEndpoint` in the MCP config for browser isolation logic

6. CLI documentation in `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` must document `--extension` under the attach command section (e.g., `playwright-cli attach --extension`), and must not document `playwright-cli open --extension` in the open command section.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
