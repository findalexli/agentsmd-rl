# Dev server hangs when `.next` directory is deleted during development

## Problem

When running `next dev`, if the `.next` output directory is deleted while the dev server is running (e.g., by running `rm -rf .next` in another terminal), the server does not detect the deletion. It continues running in a broken state — subsequent page loads may fail silently or produce undefined behavior because the build output directory is gone. The server should detect this situation and restart to recover.

## Expected Behavior

When the `.next` directory (or an ancestor directory containing it) is deleted while the dev server is running, the server should detect the deletion, log an error message via `Log.error()`, and exit with `RESTART_EXIT_CODE` so that the process manager can restart it.

The dev server startup logic already uses Watchpack to watch config files for changes. The fix should extend this existing file-watching setup to also watch the output directory and its ancestor directories for deletion.

## Requirements

- In development mode, the server must watch the `.next` output directory and its ancestor directories (up to the project root) for deletion. Watchpack's `missing` option should be used to detect when these directories are removed.
- When a watched directory is deleted, a `remove` event handler must log an error and call `process.exit(RESTART_EXIT_CODE)`.
- The `remove` handler must only trigger for paths that are actually being watched, not for every `remove` event.
- The existing config file `change` handler must only respond to changes in the actual config files, not to all file change events.

## Files to Look At

- `packages/next/src/server/lib/start-server.ts` — contains the dev server startup logic, including the Watchpack-based file watching for config file changes.
