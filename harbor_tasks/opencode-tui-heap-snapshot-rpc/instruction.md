# Capture both TUI and server heap snapshots

## Problem

The TUI has a "Write heap snapshot" command that only captures the TUI process's heap, producing a single snapshot file. For complete memory debugging, both the TUI and server (worker) process heaps need to be captured when the command is triggered.

Currently, triggering "Write heap snapshot" writes only one snapshot and displays only one file path in the toast notification. There is no mechanism for the TUI process to request a heap snapshot from the server worker process.

## Expected Behavior

When "Write heap snapshot" is triggered from the command palette:
1. The TUI process heap should be saved as `tui.heapsnapshot`
2. The server process heap should be saved as `server.heapsnapshot`
3. The toast notification should display both file paths

## Technical Context

The TUI uses a multi-process architecture across these source files:
- `packages/opencode/src/cli/cmd/tui/worker.ts` — the server worker process, exposes an RPC interface to the TUI thread
- `packages/opencode/src/cli/cmd/tui/thread.ts` — the TUI thread, communicates with the worker via an RPC client (`client.call("methodName", args)`)
- `packages/opencode/src/cli/cmd/tui/app.tsx` — the main TUI React component, renders the command palette

Heap snapshots are written using `writeHeapSnapshot()` from Node's `node:v8` (or `"v8"`) module.

The cross-process coordination requires:
- An RPC method named `snapshot` on the worker that writes the server heap to `server.heapsnapshot`
- An `onSnapshot` callback in the TUI thread that triggers both snapshot writes (TUI locally, server via RPC) and returns both file paths
- The `onSnapshot` callback must be passed as an optional prop through to the App component so the command palette can invoke it

## Changelog Command

The changelog generation instructions at `.opencode/command/changelog.md` should be restructured to organize entries into categorized sections with these exact headers:

- `# TUI`
- `# Desktop`
- `# Core`
- `# Misc`

Each subagent should append its summary to the appropriate section. The changelog output file should be `UPCOMING_CHANGELOG.md`.
