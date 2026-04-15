# Dev server hangs when `.next` directory is deleted during development

## Problem

When running `next dev`, if the `.next` output directory is deleted while the dev server is running (e.g., by running `rm -rf .next` in another terminal), the server does not detect the deletion. It continues running in a broken state — subsequent page loads may fail silently or produce undefined behavior because the build output directory is gone. The server should detect this situation and restart to recover.

## Expected Behavior

When the `.next` directory (or an ancestor directory containing it) is deleted while the dev server is running, the server should detect the deletion, log an error message, and exit with the restart exit code so that the process manager can restart it.

## Implementation Requirements

The fix must be implemented inside the `if (isDev)` block in `packages/next/src/server/lib/start-server.ts`.

### Watchpack setup

- Create a `Watchpack` instance.
- The `wp.watch()` call **must** include a `missing` option containing a list of directory paths to watch for deletion. This is in addition to the existing `files` option that watches config files.
- The path list for the `missing` option must be constructed by:
  1. Computing the absolute path of the dist directory by joining the `dir` variable with `distDir` (e.g., `path.join(dir, distDir)`).
  2. Walking ancestor directories using `path.dirname` in a loop and collecting them into an array via `.push()`.

### Deletion detection handler

- Register a Watchpack `'remove'` event handler (via `wp.on('remove', ...)`) that receives the removed path as an argument.
- The handler must guard its action with a path inclusion check — it should only trigger if the removed path is in the directory watch list (e.g., using `.includes(removedPath)` or `.indexOf(removedPath) !== -1`).
- When triggered, the handler must log an error message using `Log.error()` and then call `process.exit(RESTART_EXIT_CODE)`.

### Config file change handler

- The existing Watchpack `'change'` event handler must guard its response using a file inclusion check — it should only respond to changes in the config file list (e.g., using `.includes(filename)` or `.indexOf(filename) !== -1`), not to every file change event.

## Files to Look At

- `packages/next/src/server/lib/start-server.ts` — contains the dev server startup logic, including the Watchpack-based file watching for config file changes. The file watching setup is inside the `if (isDev)` block.
