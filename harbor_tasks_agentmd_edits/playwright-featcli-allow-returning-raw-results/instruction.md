# Add --raw flag to playwright-cli for piping output

## Problem

The `playwright-cli` tool currently wraps all command output in markdown formatting — section headers (`### Title`), code fences, page status, and generated code blocks. This makes the output human-readable but impossible to pipe into other Unix tools (like `jq`, `diff`, or shell variable capture).

For example, running `playwright-cli eval "document.title"` produces:

```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Code
\`\`\`js
document.title
\`\`\`
### Result
"Example Domain"
```

When all you want is `"Example Domain"`.

## Expected Behavior

A global `--raw` option should strip away all formatting and status sections, returning only the essential result value. When `--raw` is used:

- Only Error, Result, and Snapshot sections should be included in output
- Markdown headers (`### Title`) and code fences should be omitted
- Commands that don't produce relevant output should return nothing

This should work across the entire CLI pipeline: the option needs to flow from the CLI argument parser → session → daemon → backend → response serialization.

After implementing the code changes, update the relevant skill documentation to describe the new option and show usage examples. The project's CLI skill file should be updated to help agents understand and use this capability.

## Files to Look At

- `packages/playwright-core/src/tools/backend/response.ts` — Response class that serializes tool output into markdown sections
- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI argument parser and global options
- `packages/playwright-core/src/tools/cli-client/session.ts` — Session class that forwards commands to daemon
- `packages/playwright-core/src/tools/cli-daemon/daemon.ts` — Daemon that dispatches CLI commands to backend
- `packages/playwright-core/src/tools/backend/browserBackend.ts` — Backend that creates Response instances
- `packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts` — Generates help text for CLI
- `packages/playwright-core/src/tools/backend/evaluate.ts` — Evaluate tool (needs error handling for raw mode)
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI skill documentation
