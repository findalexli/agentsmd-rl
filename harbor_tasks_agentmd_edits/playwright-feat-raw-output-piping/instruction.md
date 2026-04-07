# feat(cli): allow returning raw results for piping

## Problem

The playwright-cli tool formats all output with markdown headers (`### Section`) and code fences (```yaml), which makes it impossible to pipe command output into other Unix tools like `jq`, `diff`, or file redirection. For example, running `playwright-cli eval "JSON.stringify(data)"` wraps the result in headers and fences, so piping to `jq` fails.

Additionally, the `evaluate` command does not properly handle errors — if the evaluated expression throws, the error is not captured in the response.

## Expected Behavior

A global `--raw` CLI option should be added that:
1. Strips all markdown formatting (no `###` headers, no code fences) from the output
2. Filters the output to only show Error, Result, and Snapshot sections (omitting Page status, generated code, etc.)
3. Returns plain text suitable for piping to other tools

The `evaluate` command should also catch errors and add them to the response.

## Files to Look At

- `packages/playwright-core/src/tools/backend/response.ts` — Response class serialize method that formats output
- `packages/playwright-core/src/tools/backend/browserBackend.ts` — Creates Response instances, passes options
- `packages/playwright-core/src/tools/backend/evaluate.ts` — Evaluate tool that needs error handling
- `packages/playwright-core/src/tools/cli-client/program.ts` — CLI argument parsing, global options
- `packages/playwright-core/src/tools/cli-client/session.ts` — Session that forwards CLI args to daemon
- `packages/playwright-core/src/tools/cli-daemon/daemon.ts` — Daemon that passes meta params to backend
- `packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts` — Help text generation
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI skill documentation

The project's CLAUDE.md and tools.md skill specify that SKILL.md must be updated when adding new CLI commands or options. Update the relevant documentation to reflect this new feature.
