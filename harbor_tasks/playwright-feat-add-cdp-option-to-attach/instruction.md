# Add --cdp option to playwright-cli attach command

## Problem

The `playwright-cli attach` command currently only supports attaching to a browser by name/endpoint via a positional argument. There is no way to connect to an existing browser (such as an Electron app launched with `--remote-debugging-port`) via its Chrome DevTools Protocol (CDP) endpoint URL.

Additionally, the `--extension` option for connecting to a browser extension is currently on the `open` command, but logically belongs on `attach` since it connects to an already-running browser rather than launching a new one.

## Expected Behavior

1. The `attach` command should accept a `--cdp <url>` option to connect to an existing browser via its CDP endpoint URL.

2. The `--extension` option should be moved from `open` to `attach`, with support for specifying a browser name (e.g., `--extension=chrome`).

3. The attach command should also accept an `--endpoint` named option as an alternative to the positional argument for specifying the target browser endpoint.

4. Conflicting usage (providing both a positional target AND named options like `--cdp`, `--endpoint`, or `--extension`) should produce an error. The error-checking condition must be exactly: `attachTarget && (args.cdp || args.endpoint || args.extension)`.

5. The following source code patterns must be present in the implementation:
   - In `packages/playwright-core/src/tools/cli-client/program.ts`: The string `'cdp'` must appear in the `globalOptions` array declaration
   - In `packages/playwright-core/src/tools/cli-daemon/commands.ts`: The attach command declared via `const attach = declareCommand` must include a `cdp` field in its options schema
   - In `packages/playwright-core/src/tools/cli-daemon/program.ts`: A `--cdp` flag must be registered via the `.option()` method
   - In `packages/playwright-core/src/tools/cli-client/session.ts`: The pattern `cliArgs.cdp` must be used when passing arguments to the daemon
   - In `packages/playwright-core/src/tools/mcp/config.ts`: The CLI `cdp` option must be mapped to `cdpEndpoint` using either `cdpEndpoint: options.cdp` or `cdpEndpoint: cliOptions.cdp`

6. CLI documentation in `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` must document `--extension` under the attach command section (e.g., `playwright-cli attach --extension`), and must not document `playwright-cli open --extension` in the open command section.
