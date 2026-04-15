# Add --cdp option to playwright-cli attach command

## Problem

The `playwright-cli attach` command currently only supports attaching to a browser by name/endpoint via a positional argument. There is no way to connect to an existing browser (such as an Electron app launched with `--remote-debugging-port`) via its Chrome DevTools Protocol (CDP) endpoint URL.

Additionally, the `--extension` option for connecting to a browser extension is currently on the `open` command, but logically belongs on `attach` since it connects to an already-running browser rather than launching a new one.

## Expected Behavior

1. The `attach` command should accept a `--cdp <url>` option to connect to an existing browser via its CDP endpoint URL
2. The `--extension` option should be moved from `open` to `attach`, with support for specifying a browser name (e.g., `--extension=chrome`)
3. The attach command should also accept an `--endpoint` named option as an alternative to the positional argument for specifying the target browser endpoint
4. Conflicting usage (providing both a positional target AND named options like `--cdp`, `--endpoint`, or `--extension`) should produce an error
5. The `cdp` option must be registered in the global CLI options array
6. The attach command's Zod schema declaration must include the `cdp` option
7. The session layer must pass the `--cdp` flag value through to the daemon
8. The config layer must map the CLI `cdp` option to an internal `cdpEndpoint` field for browser isolation logic
9. CLI documentation (SKILL.md) must document `--extension` under the attach command section, not under open

## Implementation Notes

The solution involves modifying how CLI arguments flow through the system:
- CLI argument parsing (in the client program) must include `cdp` as a recognized global option
- The attach command's schema (declared via `declareCommand`) must include a `cdp` field
- The daemon must register an `--cdp` flag via its `.option()` method
- Session code must pass the cdp argument to daemon via `cliArgs.cdp` or similar mechanism
- Config resolution must map the CLI cdp option to `cdpEndpoint` for use in browser isolation
- Conflict detection should verify that positional target and named options (`cdp`, `endpoint`, `extension`) are not provided simultaneously