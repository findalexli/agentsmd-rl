# Dev server hangs when `.next` directory is deleted during development

## Problem

When running `next dev`, if the `.next` output directory is deleted while the dev server is running (e.g., by running `rm -rf .next` in another terminal), the server does not detect the deletion. It continues running in a broken state — subsequent page loads may fail silently or produce undefined behavior because the build output directory is gone. The server should detect this situation and restart to recover.

## Expected Behavior

When the `.next` directory (or an ancestor directory containing it) is deleted while the dev server is running, the server should detect the deletion, log an error message, and exit with the restart exit code so that the process manager can restart it.

## Files to Look At

- `packages/next/src/server/lib/start-server.ts` — contains the dev server startup logic, including the Watchpack-based file watching for config file changes. The file watching setup is inside the `if (isDev)` block.
