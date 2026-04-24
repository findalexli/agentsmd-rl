# Fix Bootstrap CLI: Auto-install Deps, Resumable Flow, Timeout Handling

## Context

The `prisma bootstrap` CLI command has several UX issues that need fixing.

## Issues to Fix

### 1. Missing Dependency Detection and Auto-Install

When running `prisma bootstrap`, if `dotenv` and `prisma` packages are not installed, the CLI currently just prints a message telling the user to install them manually and re-run. It should instead offer to install them automatically.

The `detectPackageManager` function currently only checks for lock files (`pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, `deno.lock`). It should also check the `packageManager` field in `package.json` (when present) — the field contains a string like `"pnpm@10.15.1"`. The code should check whether this value starts with the package manager name (e.g., `pm.startsWith("pnpm")`). Lock files should still take priority over this field.

A new async function should be added to install development dependencies using the detected package manager.

### 2. Template Download Timeout

The template download timeout is currently too short. Increase it to 120 seconds. Also ensure timeout errors display a user-friendly message.

The decompression function should propagate errors from the underlying stream properly.

### 3. Resumable Flow for Already-Linked Projects

When running `prisma bootstrap --database db_xxx --force` on a project that's already linked, the CLI currently exits with an error. It should instead skip the link step and continue with subsequent steps (migrate/generate/seed).

## Expected Behavior

1. **Package manager detection**: When no lock file is present, detect the package manager from the `packageManager` field in package.json if present.

2. **Auto-install deps**: When missing `dotenv` or `prisma` are detected, the CLI should prompt to install them. If the user declines, show manual install instructions.

3. **Resumable flow**: When `--database` is passed on an already-linked project, skip the link step and continue.

4. **Timeout handling**: Template download timeout should be 120 seconds, and timeout errors should show a user-friendly message.

5. **Stream error handling**: The decompression function should handle errors from the underlying stream.

## Running Tests

Run the tests with:
```bash
pnpm --filter @prisma/cli test template-scaffold.vitest
pnpm --filter @prisma/cli test Bootstrap.vitest
```

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
