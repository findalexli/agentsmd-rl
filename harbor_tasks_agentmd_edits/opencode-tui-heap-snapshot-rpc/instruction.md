# Add heap snapshot functionality for TUI and server

## Problem

The TUI currently has a "Write heap snapshot" command that only captures the TUI process's heap. Users need to also capture the server process heap for complete memory debugging.

The current implementation:
1. Only writes a single heap snapshot file
2. Does not coordinate with the server worker process
3. Shows only one file path in the toast notification

## Expected Behavior

When the user triggers "Write heap snapshot" from the command palette:
1. The TUI should write its own heap snapshot to `tui.heapsnapshot`
2. An RPC call should be made to the worker to write the server heap snapshot to `server.heapsnapshot`
3. The toast notification should display both file paths

## Implementation Details

You'll need to:

1. **Add RPC method in worker** (`packages/opencode/src/cli/cmd/tui/worker.ts`):
   - Add a new `snapshot` method to the RPC object that calls `writeHeapSnapshot("server.heapsnapshot")`

2. **Implement callback in thread** (`packages/opencode/src/cli/cmd/tui/thread.ts`):
   - Import `writeHeapSnapshot` from the `v8` module
   - Add an `onSnapshot` callback to the `tui()` call that:
     - Writes the TUI heap snapshot to `tui.heapsnapshot`
     - Calls the worker's RPC `snapshot` method
     - Returns an array of both file paths

3. **Update App component** (`packages/opencode/src/cli/cmd/tui/app.tsx`):
   - Add `onSnapshot` optional prop to the `tui` function input type
   - Pass `onSnapshot` from input to the `App` component
   - Update the `App` component to accept the `onSnapshot` prop
   - Modify the "Write heap snapshot" command to call `onSnapshot` and display both file paths

4. **Update the changelog command instructions** (`.opencode/command/changelog.md`):
   - The changelog generation instructions need to be updated to organize entries into sections (TUI, Desktop, Core, Misc)
   - Update the instructions so that each subagent appends its summary to the appropriate section

## Files to Look At

- `packages/opencode/src/cli/cmd/tui/worker.ts` — Worker process RPC handlers
- `packages/opencode/src/cli/cmd/tui/thread.ts` — TUI thread that spawns the app
- `packages/opencode/src/cli/cmd/tui/app.tsx` — Main TUI app component with command palette
- `.opencode/command/changelog.md` — Instructions for the changelog generation command

## Notes

- The `writeHeapSnapshot` function is available from Node's `v8` module (or `node:v8`)
- The RPC client in thread.ts can call methods via `client.call("methodName", args)`
- The changelog command is a custom agent instruction file used by the opencode CLI
