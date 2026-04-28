# Set up Claude Code configuration for Payload CMS

## Problem

The Payload CMS repository (a pnpm monorepo using Turbo) is missing Claude Code integration. Files edited by Claude Code aren't auto-formatted, every common command triggers a permission prompt, and `CLAUDE.md` has gaps and inconsistencies.

## Code Style Requirements

This repository uses the following code quality tools. Your changes must satisfy these tools:

- **Prettier** (`prettier`): Formats markdown, JSON, YAML, JavaScript, and TypeScript files. Run `npx prettier --check <file>` to verify formatting or `npx prettier --write <file>` to auto-format.
- **ESLint** (`eslint`): Lints JavaScript and TypeScript files. Run via the monorepo's `pnpm lint` command or directly with `eslint <file>`.
- **sort-package-json**: Sorts `package.json` fields into a canonical order.

## What needs to be fixed

### 1. No post-edit formatting hook

There's no `.claude/hooks/` directory or formatting hook. When Claude Code edits a file, it doesn't get formatted — but the repo has established formatters for different file types:

- TypeScript files (`*.ts`, `*.tsx`, etc.) should be linted with `eslint --fix`
- Markdown files (`*.md`) should be formatted with `prettier --write`
- `package.json` files should be sorted with `sort-package-json`
- Other files should be formatted with `prettier --write`

Create a bash script at `.claude/hooks/post-edit.sh` that reads JSON from stdin (the format is `{"tool_input": {"file_path": "/path/to/file"}}`), extracts the file path, and dispatches to the correct formatter based on file type using bash `case` pattern matching. The script must handle edge cases gracefully — if `file_path` is null, missing, or the JSON is empty, it should exit with code 0 rather than failing.

### 2. No permission configuration

There's no `.claude/settings.json`, so every `git log`, `git diff`, `pnpm run`, or `pnpm turbo` command triggers a permission prompt. Create a Claude Code settings file that:

- Configures a `PostToolUse` hook that runs the post-edit formatting script whenever the `Edit` or `Write` tools are used
- Defines a permissions allowlist with at least 10 pre-approved command patterns, including `pnpm run` commands, `pnpm turbo` commands, and git read operations like `git log` and `git diff`

### 3. Incomplete CLAUDE.md

The existing `CLAUDE.md` has several documentation gaps:

- **Missing packages**: The `kv-redis` package isn't listed in the key directories/packages section
- **Missing storage adapter**: `R2` is not listed alongside the other storage adapters (S3, Azure, GCS, etc.) in the `storage-*` line
- **No Quick Start section**: New contributors have no quick-start guide. Add a `## Quick Start` or `### Quick Start` section that includes at least one `pnpm` command
- **Inconsistent command formatting**: Some pnpm commands use bare `pnpm build`, `pnpm dev`, `pnpm test`, or `pnpm lint` instead of the correct `pnpm run build`, `pnpm run dev`, etc. All such commands (in backtick-formatted code) should use the `pnpm run` prefix — at least 3 commands should appear this way, and none should use the bare form
- **No Turbo guidance**: There's no mention that `turbo` should be run via `pnpm turbo` rather than invoked directly. Add a note warning against running `turbo` directly

## Files to create or modify

- `.claude/hooks/post-edit.sh` — new formatting hook
- `.claude/settings.json` — new settings file
- `CLAUDE.md` — update existing documentation
