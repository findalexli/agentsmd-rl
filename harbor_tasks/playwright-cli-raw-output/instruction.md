# Allow returning raw results from playwright-cli for piping

## Problem

`playwright-cli` always wraps command output in markdown formatting: section headers (`### Title`), code fences, page status, generated code snippets, and accessibility snapshots are all included in every response. This makes it impossible to pipe CLI output into other tools (e.g., `jq`, `diff`, shell variables) because the markdown decorations pollute the data.

For example, running `playwright-cli eval "document.title"` returns something like:

```
### Page URL
https://example.com
### Generated Code
page.evaluate(...)
### Result
"Example Domain"
```

When a user only wants the raw result value `"Example Domain"`, there is no way to get it without manually parsing the markdown output.

## Expected Behavior

A global `--raw` option should be available on all `playwright-cli` commands. When `--raw` is passed:

1. Only essential result sections should be included in the output (errors, direct results, snapshots) — status information, generated code, and other decorative sections should be stripped.
2. The remaining output should be plain text without markdown headers (`###`) or code fences.
3. Commands that produce no relevant output should return empty output.

This enables workflows like:
```bash
playwright-cli --raw eval "JSON.stringify(data)" | jq '.field'
playwright-cli --raw snapshot > page.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
```

## Files to Look At

- `packages/playwright-core/src/tools/backend/response.ts` — the `Response` class that builds and serializes tool output sections
- `packages/playwright-core/src/tools/backend/browserBackend.ts` — calls the Response constructor when handling tool invocations
- `packages/playwright-core/src/tools/backend/evaluate.ts` — the evaluate tool (should handle errors gracefully in raw mode)
- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI argument parsing and global options
- `packages/playwright-core/src/tools/cli-client/session.ts` — session management, forwards options to the daemon
- `packages/playwright-core/src/tools/cli-daemon/daemon.ts` — daemon server that routes CLI commands to the backend
- `packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts` — generates `--help` output for the CLI
