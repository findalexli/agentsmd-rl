# Add a `trace close` CLI command

## Problem

The Playwright trace CLI (`npx playwright trace`) lets you open and inspect trace files, but there's no way to clean up the extracted trace data when you're done. The `openTrace` function in `traceUtils.ts` has inline cleanup logic that removes the old extracted directory before opening a new one, but this isn't exposed as a standalone operation. Users have to manually find and delete the extracted trace directory, or just open a new trace to replace it.

## Expected Behavior

There should be a `trace close` command that removes the extracted trace data directory. This gives users a clean way to free disk space when they're done inspecting a trace.

The cleanup logic already exists inline in `openTrace` — it should be extracted into a reusable function so that both `openTrace` and the new `close` command can share it.

After implementing the command, update the trace CLI's documentation to reflect the new capability. The SKILL.md file in the trace tools directory documents all available trace commands and the recommended workflow — it should be kept in sync.

## Files to Look At

- `packages/playwright-core/src/tools/trace/traceUtils.ts` — trace extraction and cleanup utilities
- `packages/playwright-core/src/tools/trace/traceCli.ts` — CLI command registration for trace subcommands
- `packages/playwright-core/src/tools/trace/SKILL.md` — documentation for trace CLI commands and workflow
